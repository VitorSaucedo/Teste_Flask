from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta_da_aplicacao'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), unique=True, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    todos = db.relationship('Todo', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String(50), default='Geral')
    priority = db.Column(db.String(20), default='Média')
    tags = db.Column(db.String(200), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    subtasks = db.relationship('Subtask', backref='parent_task', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return '<Task %r>' % self.id
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'description': self.description,
            'completed': self.completed,
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'category': self.category,
            'priority': self.priority,
            'tags': self.tags,
            'user_id': self.user_id,
            'subtasks': [subtask.to_dict() for subtask in self.subtasks]
        }

class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)
    
    def __repr__(self):
        return '<Subtask %r>' % self.id
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'completed': self.completed,
            'date_created': self.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'todo_id': self.todo_id
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_and_update_db():
    db_path = 'todo.db'
    
    # Verificar se o banco de dados existe
    if os.path.exists(db_path):
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se as tabelas existem
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall() if table[0] != 'sqlite_sequence']
            
            # Verificar se as tabelas necessárias existem
            if 'user' not in tables:
                print("Criando tabela de usuários...")
                # Não fazemos nada aqui, deixamos o db.create_all() criar a tabela
            
            if 'subtask' not in tables:
                print("Criando tabela de subtarefas...")
                # Não fazemos nada aqui, deixamos o db.create_all() criar a tabela
            
            # Se a tabela todo existe, verificamos as colunas
            if 'todo' in tables:
                # Verificar se as colunas novas existem
                cursor.execute("PRAGMA table_info(todo)")
                columns = [column[1] for column in cursor.fetchall()]
                
                # Adicionar colunas que faltam
                if 'description' not in columns:
                    cursor.execute("ALTER TABLE todo ADD COLUMN description TEXT DEFAULT ''")
                if 'due_date' not in columns:
                    cursor.execute("ALTER TABLE todo ADD COLUMN due_date DATE")
                if 'category' not in columns:
                    cursor.execute("ALTER TABLE todo ADD COLUMN category VARCHAR(50) DEFAULT 'Geral'")
                if 'priority' not in columns:
                    cursor.execute("ALTER TABLE todo ADD COLUMN priority VARCHAR(20) DEFAULT 'Média'")
                if 'tags' not in columns:
                    cursor.execute("ALTER TABLE todo ADD COLUMN tags VARCHAR(200) DEFAULT ''")
                if 'user_id' not in columns:
                    cursor.execute("ALTER TABLE todo ADD COLUMN user_id INTEGER")
            
            # Salvar alterações
            conn.commit()
            conn.close()
            print("Banco de dados migrado com sucesso!")
        except Exception as e:
            print(f"Erro ao migrar o banco de dados: {e}")
            
            # Se ocorrer algum erro, tenta recriar o banco de dados
            try:
                conn.close()
            except:
                pass
            
            with app.app_context():
                db.create_all()
                print("Banco de dados recriado com sucesso!")
    else:
        # Se o banco de dados não existe, cria um novo
        with app.app_context():
            db.create_all()
            print("Banco de dados criado com sucesso!")

# Verificar e atualizar o banco de dados antes de iniciar a aplicação
check_and_update_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first() if email else None
        
        if user_exists:
            flash('Nome de usuário já existe!', 'danger')
            return render_template('register.html')
        
        if email and email_exists:
            flash('Email já está em uso!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem!', 'danger')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, name=name, email=email)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Conta criada com sucesso! Agora você pode fazer login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Por favor, verifique suas credenciais e tente novamente.', 'danger')
            return render_template('login.html')
        
        login_user(user, remember=remember)
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if email != current_user.email:
            email_exists = User.query.filter_by(email=email).first()
            if email_exists:
                flash('Email já está em uso!', 'danger')
                return render_template('profile.html')
        
        if current_password and new_password:
            if not check_password_hash(current_user.password, current_password):
                flash('Senha atual incorreta!', 'danger')
                return render_template('profile.html')
            
            if new_password != confirm_password:
                flash('As novas senhas não coincidem!', 'danger')
                return render_template('profile.html')
            
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        
        current_user.name = name
        current_user.email = email
        
        try:
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
        except:
            flash('Ocorreu um erro ao atualizar o perfil.', 'danger')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_description = request.form.get('description', '')
        task_due_date_str = request.form.get('due_date', '')
        task_category = request.form.get('category', 'Geral')
        task_priority = request.form.get('priority', 'Média')
        task_tags = request.form.get('tags', '')
        
        task_due_date = None
        if task_due_date_str:
            try:
                task_due_date = datetime.strptime(task_due_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
                
        if task_content.strip():
            new_task = Todo(
                content=task_content,
                description=task_description,
                due_date=task_due_date,
                category=task_category,
                priority=task_priority,
                tags=task_tags,
                user_id=current_user.id
            )
            try:
                db.session.add(new_task)
                db.session.commit()
                
                # Se for uma requisição AJAX, retorna apenas a nova tarefa
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return render_template('_task_item.html', task=new_task, today=date.today())
                
                return redirect('/')
            except:
                return 'Houve um problema ao adicionar sua tarefa'
        else:
            return redirect('/')
    else:
        # Passar a data atual para o template
        today = date.today()
        
        # Filtrar tarefas somente do usuário atual
        tasks = Todo.query.filter_by(user_id=current_user.id).order_by(Todo.date_created).all()
        categories = db.session.query(Todo.category).filter_by(user_id=current_user.id).distinct().all()
        categories = [c[0] for c in categories]
        if 'Geral' not in categories:
            categories.append('Geral')
        
        filter_category = request.args.get('category', '')
        filter_priority = request.args.get('priority', '')
        
        query = Todo.query.filter_by(user_id=current_user.id)
        if filter_category:
            query = query.filter(Todo.category == filter_category)
        if filter_priority:
            query = query.filter(Todo.priority == filter_priority)
            
        tasks = query.order_by(Todo.date_created).all()
        
        # Se for uma requisição AJAX, retornar apenas a lista de tarefas
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render_template('_task_list.html', 
                                  tasks=tasks, 
                                  categories=categories,
                                  priorities=['Alta', 'Média', 'Baixa'],
                                  today=today)
        
        return render_template('index.html', 
                               tasks=tasks, 
                               categories=categories,
                               priorities=['Alta', 'Média', 'Baixa'],
                               today=today)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    
    # Verificar se a tarefa pertence ao usuário atual
    if task_to_delete.user_id != current_user.id:
        flash('Você não tem permissão para excluir esta tarefa.', 'danger')
        return redirect('/')
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um problema ao excluir essa tarefa'

@app.route('/complete/<int:id>')
@login_required
def complete(id):
    task = Todo.query.get_or_404(id)
    
    # Verificar se a tarefa pertence ao usuário atual
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect('/')
    
    task.completed = not task.completed
    
    try:
        db.session.commit()
        
        # Se for uma requisição AJAX, retorna JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'task_id': id,
                'completed': task.completed
            })
        
        return redirect('/')
    except:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False}), 500
        return 'Houve um problema ao atualizar essa tarefa'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    task = Todo.query.get_or_404(id)
    
    # Verificar se a tarefa pertence ao usuário atual
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect('/')
    
    categories = db.session.query(Todo.category).filter_by(user_id=current_user.id).distinct().all()
    categories = [c[0] for c in categories]
    if 'Geral' not in categories:
        categories.append('Geral')
    
    if request.method == 'POST':
        task.content = request.form['content']
        task.description = request.form.get('description', '')
        task_due_date_str = request.form.get('due_date', '')
        task.category = request.form.get('category', 'Geral')
        task.priority = request.form.get('priority', 'Média')
        task.tags = request.form.get('tags', '')
        
        if task_due_date_str:
            try:
                task.due_date = datetime.strptime(task_due_date_str, '%Y-%m-%d').date()
            except ValueError:
                task.due_date = None
        else:
            task.due_date = None
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Houve um problema ao atualizar essa tarefa'
    else:
        return render_template('update.html', 
                               task=task, 
                               categories=categories,
                               priorities=['Alta', 'Média', 'Baixa'])

@app.route('/api/tasks')
@login_required
def api_tasks():
    tasks = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect('/')
    
    tasks = Todo.query.filter(
        (Todo.user_id == current_user.id) &
        ((Todo.content.like(f'%{query}%')) | 
        (Todo.description.like(f'%{query}%')) |
        (Todo.tags.like(f'%{query}%')))
    ).all()
    
    categories = db.session.query(Todo.category).filter_by(user_id=current_user.id).distinct().all()
    categories = [c[0] for c in categories]
    if 'Geral' not in categories:
        categories.append('Geral')
    
    # Passar a data atual para o template
    today = date.today()
    
    # Se for uma requisição AJAX, retornar apenas a lista de tarefas
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('_task_list.html', 
                              tasks=tasks, 
                              categories=categories,
                              search_query=query,
                              priorities=['Alta', 'Média', 'Baixa'],
                              today=today)
    
    return render_template('index.html', 
                           tasks=tasks, 
                           categories=categories,
                           search_query=query,
                           priorities=['Alta', 'Média', 'Baixa'],
                           today=today)

@app.route('/statistics')
@login_required
def statistics():
    total_tasks = Todo.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Todo.query.filter_by(user_id=current_user.id, completed=True).count()
    
    categories = db.session.query(Todo.category).filter_by(user_id=current_user.id).distinct().all()
    categories = [c[0] for c in categories]
    
    category_stats = []
    for category in categories:
        category_count = Todo.query.filter_by(user_id=current_user.id, category=category).count()
        category_completed = Todo.query.filter_by(user_id=current_user.id, category=category, completed=True).count()
        category_stats.append({
            'name': category,
            'count': category_count,
            'completed': category_completed,
            'percentage': round((category_completed / category_count) * 100) if category_count > 0 else 0
        })
    
    priority_stats = []
    for priority in ['Alta', 'Média', 'Baixa']:
        priority_count = Todo.query.filter_by(user_id=current_user.id, priority=priority).count()
        priority_completed = Todo.query.filter_by(user_id=current_user.id, priority=priority, completed=True).count()
        priority_stats.append({
            'name': priority,
            'count': priority_count,
            'completed': priority_completed,
            'percentage': round((priority_completed / priority_count) * 100) if priority_count > 0 else 0
        })
    
    # Tarefas por mês
    monthly_tasks = {}
    tasks = Todo.query.filter_by(user_id=current_user.id).all()
    for task in tasks:
        month_year = task.date_created.strftime('%Y-%m')
        if month_year in monthly_tasks:
            monthly_tasks[month_year]['total'] += 1
            if task.completed:
                monthly_tasks[month_year]['completed'] += 1
        else:
            monthly_tasks[month_year] = {
                'month': task.date_created.strftime('%b %Y'),
                'total': 1,
                'completed': 1 if task.completed else 0
            }
    
    # Adicionar contagem de tarefas atrasadas
    today = date.today()
    overdue_tasks = Todo.query.filter(
        Todo.user_id == current_user.id,
        Todo.completed == False,
        Todo.due_date < today,
        Todo.due_date != None
    ).count()
    
    return render_template(
        'statistics.html',
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0,
        category_stats=category_stats,
        priority_stats=priority_stats,
        monthly_stats=list(monthly_tasks.values()),
        overdue_tasks=overdue_tasks
    )

# Rotas para gerenciar subtarefas
@app.route('/subtask/add/<int:todo_id>', methods=['POST'])
@login_required
def add_subtask(todo_id):
    task = Todo.query.get_or_404(todo_id)
    
    # Verificar se a tarefa pertence ao usuário atual
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect('/')
    
    content = request.form.get('subtask_content', '')
    
    if content.strip():
        new_subtask = Subtask(content=content, todo_id=todo_id)
        
        try:
            db.session.add(new_subtask)
            db.session.commit()
        except:
            flash('Houve um problema ao adicionar a subtarefa.', 'danger')
    
    # Redirecionar para a página de atualização da tarefa principal
    return redirect(url_for('update', id=todo_id))

@app.route('/subtask/complete/<int:subtask_id>/<int:todo_id>')
@login_required
def complete_subtask(subtask_id, todo_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    task = Todo.query.get_or_404(todo_id)
    
    # Verificar se a tarefa pertence ao usuário atual
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect('/')
    
    subtask.completed = not subtask.completed
    
    try:
        db.session.commit()
        
        # Se for uma requisição AJAX, retorna JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Calcular o número de subtarefas concluídas para atualizar o progresso
            total_subtasks = len(task.subtasks)
            completed_subtasks = sum(1 for s in task.subtasks if s.completed)
            percentage = round((completed_subtasks / total_subtasks) * 100) if total_subtasks > 0 else 0
            
            return jsonify({
                'success': True,
                'subtask_id': subtask_id,
                'todo_id': todo_id,
                'completed': subtask.completed,
                'completed_count': completed_subtasks,
                'total_count': total_subtasks,
                'percentage': percentage
            })
            
    except:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False}), 500
        flash('Houve um problema ao atualizar a subtarefa.', 'danger')
    
    return redirect(url_for('update', id=todo_id))

@app.route('/subtask/delete/<int:subtask_id>/<int:todo_id>')
@login_required
def delete_subtask(subtask_id, todo_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    task = Todo.query.get_or_404(todo_id)
    
    # Verificar se a tarefa pertence ao usuário atual
    if task.user_id != current_user.id:
        flash('Você não tem permissão para modificar esta tarefa.', 'danger')
        return redirect('/')
    
    try:
        db.session.delete(subtask)
        db.session.commit()
    except:
        flash('Houve um problema ao excluir a subtarefa.', 'danger')
    
    return redirect(url_for('update', id=todo_id))

if __name__ == '__main__':
    app.run(debug=True)
