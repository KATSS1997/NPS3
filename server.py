import http.server
import socketserver
import cx_Oracle
import json

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/confirm':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            numero_os = data.get('osNumber')

            print('Recebido número da OS para confirmação:', numero_os)

            try:
                # Conectar ao banco de dados Oracle
                dsn_tns = cx_Oracle.makedsn('172.16.10.7', '1521', service_name='prd')
                conn_oracle = cx_Oracle.connect(user='dbamv', password='cmdmvfbg190918', dsn=dsn_tns)
                cursor_oracle = conn_oracle.cursor()

                # Verifica se a OS existe no Oracle
                cursor_oracle.execute("SELECT COUNT(*) FROM SOLICITACAO_OS WHERE CD_OS = :osNumber", osNumber=numero_os)
                row_oracle = cursor_oracle.fetchone()
                if row_oracle[0] == 0:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Esta OS não existe no sistema Oracle.'}).encode())
                    print('Esta OS não existe no sistema Oracle:', numero_os)
                    return

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'OS disponível para avaliação.'}).encode())
                print('OS disponível para avaliação:', numero_os)

                conn_oracle.close()
            except cx_Oracle.DatabaseError as e:
                error_message = f"Erro ao conectar ao banco de dados Oracle: {e}"
                print(error_message)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': error_message}).encode())

        elif self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            numero_os = data.get('osNumber')
            avaliacao = data.get('rating')
            solicitacao_atendida = data.get('requestAnswered')
            comentario = data.get('comment')

            print('Recebido número da OS para inserção:', numero_os)
            print('Recebida avaliação:', avaliacao)
            print('Recebida informação sobre solicitação atendida:', solicitacao_atendida)
            print('Recebido comentário:', comentario)

            try:
                # Conectar ao banco de dados Oracle
                dsn_tns = cx_Oracle.makedsn('172.16.10.7', '1521', service_name='prd')
                conn_oracle = cx_Oracle.connect(user='dbamv', password='cmdmvfbg190918', dsn=dsn_tns)
                cursor_oracle = conn_oracle.cursor()

                # Verifica se já existe uma avaliação para a mesma OS
                cursor_oracle.execute("SELECT COUNT(*) FROM OrdensServico WHERE NumeroOS = :osNumber", osNumber=numero_os)
                row_oracle = cursor_oracle.fetchone()
                if row_oracle[0] > 0:
                    conn_oracle.close()
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Esta OS já foi avaliada anteriormente.'}).encode())
                    print('Esta OS já foi avaliada anteriormente:', numero_os)
                    return

                # Insere a nova avaliação
                cursor_oracle.execute("INSERT INTO OrdensServico (NumeroOS, Avaliacao, SolicitacaoAtendida, Comentario) "
                                      "VALUES (:osNumber, :avaliacao, :solicitacao_atendida, :comentario)",
                                      osNumber=numero_os, avaliacao=avaliacao, solicitacao_atendida=solicitacao_atendida,
                                      comentario=comentario)
                conn_oracle.commit()
                conn_oracle.close()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Avaliação registrada com sucesso.'}).encode())
                print('Avaliação registrada com sucesso para OS:', numero_os)
            except cx_Oracle.DatabaseError as e:
                error_message = f"Erro ao conectar ao banco de dados Oracle: {e}"
                print(error_message)
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': error_message}).encode())

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print("Servindo na porta", PORT)
    httpd.serve_forever()
