@app.route('/input', methods=['GET', 'POST'])
def input_data():
    categories = Category.query.all()

    if request.method == 'POST':
        category_id = request.form.get('category')
        question = request.form.get('question')
        answer = request.form.get('answer')

        # Optional: add more dynamic fields from schema later if needed
        field_data = {
            'question': question,
            'answer': answer
        }

        new_entry = Entry(category_id=category_id, field_data=field_data)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('input_data'))

    entries = Entry.query.all()
    return render_template('input.html', categories=categories, all_data=entries)