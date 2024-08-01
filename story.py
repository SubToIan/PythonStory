from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key="sk-proj-418yuqNf2J1kqvnnFIimT3BlbkFJSSTeZ7wSSRZmxv33kU4m"
)

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/generate', methods=['POST'])
def generate_story():
    # 사용자가 입력한 주제를 가져옴
    topic = request.form['topic']

    # GPT API 요청을 위한 메시지 설정
    messages = [
        {'role': 'system', 'content': '당신은 창의적인 이야기 작가입니다. 주어진 주제에 따라 이야기를 생성하세요.'},
        {'role': 'user', 'content': f'주제: {topic}'}
    ]

    # GPT API 호출
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # 응답에서 이야기 추출
    story = response.choices[0].message.content

    return render_template('result.html', topic=topic, story=story)

if __name__ == '__main__':
    app.run(debug=True)