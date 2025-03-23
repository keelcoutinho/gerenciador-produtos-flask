from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///produtos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Swagger(app)
db = SQLAlchemy(app)

# Middleware para permitir CORS manualmente
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # Permite todas as origens
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
    return response

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    valor = valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

# Rota para cadastrar os produtos
@app.route('/produto', methods=['POST'])
def cadastrar_produto():
    """
    Cadastrar um novo produto
    ---
    tags:
      - Produtos
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: imagem
        in: formData
        type: string
        required: true
        description: URL da imagem do produto
        example: "https://meusite.com/produto.jpg"
      - name: nome
        in: formData
        type: string
        required: true
        description: Nome do produto
        example: "Produto Teste"
      - name: valor
        in: formData
        type: number
        required: true
        description: Preço do produto
        example: 199.99
      - name: descricao
        in: formData
        type: string
        required: true
        description: Descrição do produto
        example: "Descrição do produto"
    responses:
      201:
        description: Produto cadastrado com sucesso
      400:
        description: Erro nos dados enviados
    """
    try:
        # Convertendo os dados para JSON
        data = {
            "imagem": request.form.get('imagem'),
            "nome": request.form.get('nome'),
            "valor": request.form.get('valor'),
            "descricao": request.form.get('descricao')
        }
        
        novo_produto = Produto(
            imagem=data['imagem'],
            nome=data['nome'],
            valor=data['valor'],
            descricao=data['descricao']
        )

        db.session.add(novo_produto)
        db.session.commit()

        return jsonify({"message": "Produto cadastrado com sucesso"}), 201
    
    except Exception as e:
        return jsonify({"error": f"Erro ao cadastrar produto: {str(e)}"}), 400

# Rota para listar os produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    """
    Lista todos os produtos cadastrados
    ---
    tags:
      - Produtos
    responses:
      200:
        description: Lista de produtos
    """
    produtos = Produto.query.all()
    resultado = [{"id": p.id, "imagem": p.imagem, "nome": p.nome, "valor": p.valor, "descricao": p.descricao} for p in produtos]
    return jsonify(resultado)

# Rota para obter um produto específico pelo ID
@app.route('/produto/<int:id>', methods=['GET'])
def obter_produto(id):
    """
    Retorna um produto pelo ID
    ---
    tags:
      - Produtos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do produto a ser buscado
    responses:
      200:
        description: Produto encontrado
      404:
        description: Produto não encontrado
    """
    produto = Produto.query.get(id)
    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404

    return jsonify({
        "id": produto.id,
        "imagem": produto.imagem,
        "nome": produto.nome,
        "valor": produto.valor,
        "descricao": produto.descricao
    }), 200

# Rota para atualizar os produtos
@app.route('/produto/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    """
    Atualizar um produto existente
    ---
    tags:
      - Produtos
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: id
        in: path
        type: integer
        required: true 
        description: ID do produto a ser atualizado
      - name: imagem
        in: formData
        type: string
        required: false
        description: Nova URL da imagem do produto
        example: "https://meusite.com/novo-produto.jpg"
      - name: nome
        in: formData
        type: string
        required: false
        description: Novo nome do produto
        example: "Novo Nome do Produto"
      - name: valor
        in: formData
        type: number
        required: false
        description: Novo preço do produto
        example: 299.99
      - name: descricao
        in: formData
        type: string
        required: false
        description: Nova descrição do produto
        example: "Nova descrição do produto"
    responses:
      200:
        description: Produto atualizado com sucesso
      404:
        description: Produto não encontrado
      400:
        description: Erro ao atualizar produto
    """
    produto = Produto.query.get(id)
    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404

    try:
        # Atualiza apenas os campos que foram enviados
        if request.form.get('imagem'):
            produto.imagem = request.form.get('imagem')
        if request.form.get('nome'):
            produto.nome = request.form.get('nome')
        if request.form.get('valor'):
            produto.valor = float(request.form.get('valor'))
        if request.form.get('descricao'):
            produto.descricao = request.form.get('descricao')

        db.session.commit()
        return jsonify({"message": "Produto atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar produto: {str(e)}"}), 400

# Rota para deletar os produtos
@app.route('/produto/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    """
    Remove um produto
    ---
    tags:
      - Produtos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Produto removido com sucesso
      404:
        description: Produto não encontrado
    """
    produto = Produto.query.get(id)
    # Verifica se o produto existe antes de deletar
    if not produto:
        return jsonify({"message": "Produto não encontrado"}), 404
    db.session.delete(produto)
    db.session.commit()
    return jsonify({"message": "Produto removido com sucesso"})

if __name__ == '__main__':
    app.run(debug=True)