import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    theme = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)

    options = relationship("Option", back_populates="question")


class Option(Base):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    option_text = Column(String, nullable=False)

    question = relationship("Question", back_populates="options")


def initialize_database():
    engine = create_engine('sqlite:///quiz.db', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with open('questions.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            existing_question = session.query(Question).filter_by(
                theme=item['theme'],
                question_text=item['question'],
                correct_answer=item['correct_answer']
            ).first()

            if not existing_question:
                new_question = Question(
                    theme=item['theme'],
                    question_text=item['question'],
                    correct_answer=item['correct_answer']
                )

                for option_text in item['options']:
                    new_option = Option(option_text=option_text)
                    new_question.options.append(new_option)
                session.add(new_question)
            else:
                print(f"Вопрос уже существует: {item['question']}")

        session.commit()
    except FileNotFoundError:
        print("Файл questions.json не найден.")
    finally:
        session.close()


if __name__ == "__main__":
    initialize_database()
