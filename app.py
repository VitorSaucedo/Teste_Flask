from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
            'tags': self.tags
        }

def check_and_update_db():
    db_path = 'todo.db'
    
    # Verificar se o banco de dados existe
    if os.path.exists(db_path):
        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
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
                
            os.remove(db_path)
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

@app.route('/', methods=['POST', 'GET'])
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
                tags=task_tags
            )
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return 'Houve um problema ao adicionar sua tarefa'
        else:
            return redirect('/')
    else:
        # Passar a data atual para o template
        today = date.today()
        
        tasks = Todo.query.order_by(Todo.date_created).all()
        categories = db.session.query(Todo.category).distinct().all()
        categories = [c[0] for c in categories]
        if 'Geral' not in categories:
            categories.append('Geral')
        
        filter_category = request.args.get('category', '')
        filter_priority = request.args.get('priority', '')
        
        query = Todo.query
        if filter_category:
            query = query.filter(Todo.category == filter_category)
        if filter_priority:
            query = query.filter(Todo.priority == filter_priority)
            
        tasks = query.order_by(Todo.date_created).all()
        
        return render_template('index.html', 
                               tasks=tasks, 
                               categories=categories,
                               priorities=['Alta', 'Média', 'Baixa'],
                               today=today)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um problema ao excluir essa tarefa'

@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)
    task.completed = not task.completed
    
    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um problema ao atualizar essa tarefa'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    categories = db.session.query(Todo.category).distinct().all()
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
def api_tasks():
    tasks = Todo.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect('/')
    
    tasks = Todo.query.filter(
        (Todo.content.like(f'%{query}%')) | 
        (Todo.description.like(f'%{query}%')) |
        (Todo.tags.like(f'%{query}%'))
    ).all()
    
    categories = db.session.query(Todo.category).distinct().all()
    categories = [c[0] for c in categories]
    if 'Geral' not in categories:
        categories.append('Geral')
    
    # Passar a data atual para o template
    today = date.today()
    
    return render_template('index.html', 
                           tasks=tasks, 
                           categories=categories,
                           search_query=query,
                           priorities=['Alta', 'Média', 'Baixa'],
                           today=today)

@app.route('/statistics')
def statistics():
    total_tasks = Todo.query.count()
    completed_tasks = Todo.query.filter_by(completed=True).count()
    
    categories = db.session.query(Todo.category).distinct().all()
    categories = [c[0] for c in categories]
    
    category_stats = []
    for category in categories:
        category_total = Todo.query.filter_by(category=category).count()
        category_completed = Todo.query.filter_by(category=category, completed=True).count()
        if category_total > 0:
            completion_rate = (category_completed / category_total) * 100
        else:
            completion_rate = 0
        
        category_stats.append({
            'name': category,
            'total': category_total,
            'completed': category_completed,
            'completion_rate': round(completion_rate, 1)
        })
    
    # Tarefas atrasadas
    today = date.today()
    overdue_tasks = Todo.query.filter(
        (Todo.due_date < today) & (Todo.completed == False)
    ).count()
    
    return render_template('statistics.html', 
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           completion_rate=round((completed_tasks/total_tasks)*100, 1) if total_tasks > 0 else 0,
                           category_stats=category_stats,
                           overdue_tasks=overdue_tasks)

if __name__ == "__main__":
    app.run(debug=True)
