from flask import Flask, request, jsonify, render_template
import language_tool_python
import html

app = Flask(__name__)
tool = language_tool_python.LanguageToolPublicAPI('en-US')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    original_text = data['text']
    matches = tool.check(original_text)
    corrected_text = tool.correct(original_text)

    # Escape original text for HTML
    highlighted_input = html.escape(original_text)
    offset_shift = 0
    for match in matches:
        start = match.offset + offset_shift
        end = start + match.errorLength
        error_text = highlighted_input[start:end]
        span = f"<span style='background-color:#ffd6d6'>{error_text}</span>"
        highlighted_input = highlighted_input[:start] + span + highlighted_input[end:]
        offset_shift += len(span) - len(error_text)

    # Highlight changes in green
    output_words = corrected_text.split()
    input_words = original_text.split()

    highlighted_corrected = []
    for i, word in enumerate(output_words):
        if i < len(input_words) and word != input_words[i]:
            highlighted_corrected.append(f"<span style='background-color:#d6ffd6'>{html.escape(word)}</span>")
        else:
            highlighted_corrected.append(html.escape(word))
    highlighted_output = ' '.join(highlighted_corrected)

    word_count = len(original_text.strip().split())
    accuracy_percent = max(0, int((1 - len(matches) / word_count) * 100)) if word_count else 100

    return jsonify({
        'highlighted_input': highlighted_input,
        'highlighted_output': highlighted_output,
        'accuracy_percent': accuracy_percent,
        'word_count': word_count
    })

if __name__ == '__main__':
    app.run(debug=True)

