import gensim
import http.server
import socketserver
import json
from data_preprocessor import DataPreprocessor

model_Q = gensim.models.Doc2Vec.load("models/model_Q_vector_size_100_window_5_min_count_5_workers_20_epochs_100_negative_15_sample_1e-5_dm_0")
model_A = gensim.models.Doc2Vec.load("models/model_A_vector_size_100_window_5_min_count_5_workers_20_epochs_100_negative_15_sample_1e-5_dm_0")
model_QA = gensim.models.Doc2Vec.load("models/model_QA_vector_size_100_window_5_min_count_5_workers_20_epochs_100_negative_15_sample_1e-5_dm_0")

PORT = 7999
preprocessor = DataPreprocessor(None)

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.headers)
        self.send_response(404)
        self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        self.send_response(200)
        self.send_header('Content-type', 'text/json; charset=utf-8')
        msg = 'invalid post type'
        post_input = preprocessor.full_preprocess(post_data['input'])
        if post_data['debug'] == 'true':
            print(self.headers)
            print(post_data)
            print(post_input)
        if post_data['type'] == 'Q':
            msg = json.dumps(list(map(float, model_Q.infer_vector(post_input, epochs=100))))
        elif post_data['type'] == 'A':
            msg = json.dumps(list(map(float, model_A.infer_vector(post_input, epochs=100))))
        elif post_data['type'] == 'QA':
            msg = json.dumps(list(map(float, model_QA.infer_vector(post_input, epochs=100))))
        self.send_header('Content-length', len(msg))
        self.end_headers()
        self.wfile.write(bytes(msg, 'utf8'))


with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
    try:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
        httpd.server_close()
        print("Server stopped.")

