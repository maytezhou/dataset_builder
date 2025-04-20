import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
from config import Config
from models import db, DatasetSchema, Entry,Category
import io

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        fields = request.form.get('fields').split(',')
        category_names = request.form.get('category').split(',')

        # Save categories
        categories = []
        for name in category_names:
            name = name.strip()
            if name:  # avoid empty names
                existing = Category.query.filter_by(name=name).first()
                if not existing:
                    category = Category(name=name)
                    db.session.add(category)
                    db.session.flush()  # get ID before commit
                    categories.append(category)
                else:
                    categories.append(existing)

        db.session.commit()

        # Save schema fields for each category
        for category in categories:
            for field in fields:
                db.session.add(DatasetSchema(field_name=field.strip(), category_id=category.id))

        db.session.commit()
        return redirect(url_for('input_data'))

    return render_template('setup.html')

@app.route('/input', methods=['GET', 'POST'])
def input_data():
    categories = Category.query.all()

    if request.method == 'POST':
        category_id = request.form.get('category')
        question = request.form.get('question')
        answer = request.form.get('answer')

        # Save question & answer in field_data
        field_data = {
            'question': question,
            'answer': answer
        }

        new_entry = Entry(category_id=category_id, field_data=field_data)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('input_data'))

    # --- Handle GET + Search ---
    search_query = request.args.get('search', '').strip()
    if search_query:
        entries = Entry.query.all()
        filtered = []
        for entry in entries:
            question = entry.field_data.get('question', '')
            answer = entry.field_data.get('answer', '')
            category_name = entry.category.name if entry.category else ''

            # Search across question, answer, and category name
            if (
                search_query.lower() in question.lower()
                or search_query.lower() in answer.lower()
                or search_query.lower() in category_name.lower()
            ):
                filtered.append(entry)

        results = filtered
    else:
        results = []

    entries = Entry.query.all()
    return render_template(
        'input.html',
        categories=categories,
        all_data=entries,
        results=results
    )

@app.route('/view_db')
def view_db():
    entries = Entry.query.all()
    return render_template('view_db.html', entries=entries)


@app.route('/export', methods=['POST'])
def export_excel():
    entries = Entry.query.all()

    if not entries:
        return "No data to export", 400

    # Assuming each entry has a dictionary in .field_data and a .category
    data = []
    for entry in entries:
        row = entry.field_data.copy()
        row['Category'] = entry.category.name if entry.category else "Uncategorized"
        data.append(row)

    df = pd.DataFrame(data)

    # Save to an in-memory buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dataset')

    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='dataset.xlsx'
    )



if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


