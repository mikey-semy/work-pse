from typing import List
import json
from sqlalchemy import select, func

from app.models.questions import QuestionModel
from app.schemas.questions import QuestionSchema
from app.services.base import BaseService, BaseDataManager

class QuestionService(BaseService):

    async def question_exists(self, question_text: str) -> bool:
        question = await QuestionDataManager(self.session).get_question_by_text(question_text)
        return question is not None
    async def add_question(self, question: QuestionSchema) -> QuestionSchema:
        
        if await self.question_exists(question.question_text):
            raise ValueError("Вопрос уже существует в базе данных.")

        new_question = QuestionModel(
            question_type=question.question_type,
            question_text=question.question_text,
            answers=question.answers,
            correct_answers=question.correct_answers
        )
        return await QuestionDataManager(self.session).add_question(new_question)
    
    async def add_all_questions(self) -> None:
        with open('app/data/questions.json', 'r', encoding='utf-8') as file:
            questions = json.load(file)

        for question in questions:
            question_data = json.loads(list(question.values())[0])
            new_question = QuestionModel(
                    question_text=question_data.get('questionText', ''),
                    answers=question_data.get('answerText', []),
                    correct_answers=question_data.get('correctAnswerText', [])
                )
            await QuestionDataManager(self.session).add_question(new_question)
            
    async def update_question(self, question_id: int, updated_question: QuestionSchema
                              ) -> QuestionSchema:
        updated_question = QuestionModel(
            question_type=updated_question.question_type,
            question_text=updated_question.question_text,
            answers=updated_question.answers,
            correct_answers=updated_question.correct_answers
        )
        return await QuestionDataManager(self.session).update_question(question_id, updated_question)

    async def update_question_by_text(self, q: str, updated_question: QuestionSchema
                              ) -> QuestionSchema:
        updated_question = QuestionModel(
            question_type=updated_question.question_type,
            question_text=updated_question.question_text,
            answers=updated_question.answers,
            correct_answers=updated_question.correct_answers
        )
        return await QuestionDataManager(self.session).update_question_by_text(q, updated_question)
    
    async def get_question(self, question_id: int) -> QuestionSchema:
        return await QuestionDataManager(self.session).get_question(question_id)

    async def get_questions(self) -> List[QuestionSchema]:
        return await QuestionDataManager(self.session).get_questions()

    async def get_quantity(self) -> int:
        result = await QuestionDataManager(self.session).get_questions()
        return len(result)
    
    async def get_duplicates(self) -> int:
        return await QuestionDataManager(self.session).get_duplicate_count_by_question_text()
    
    async def search_questions(self, q: str) -> List[QuestionSchema]:
        return await QuestionDataManager(self.session).search_questions(q)

class QuestionDataManager(BaseDataManager):
    async def add_question(self, new_question) -> QuestionSchema:
        return await self.add_one(new_question)

    async def update_question(self,
                              question_id: int,
                              updated_question: QuestionSchema) -> QuestionSchema | None:
        old_question = await self.get_question(question_id)
        schema: QuestionSchema = await self.update_one(old_question, updated_question)
        return schema

    async def update_question_by_text(self,
                              q: str,
                              updated_question: QuestionSchema) -> QuestionSchema | None:
        old_questions = await self.search_questions(q)

        if not old_questions:  # Проверка на пустой список
            return None
    
        # Если найдено несколько вопросов, выбираем первый
        old_question = old_questions[0]  # Берем только первый вопрос

        # Преобразование Pydantic схемы в SQLAlchemy модель
        question_to_update = await self.get_question(old_question.id)  # Получаем SQLAlchemy модель по ID

        # Обновляем поля модели
        question_to_update.question_type = updated_question.question_type
        question_to_update.question_text = updated_question.question_text
        question_to_update.answers = updated_question.answers
        question_to_update.correct_answers = updated_question.correct_answers

        schema: QuestionSchema = await self.update_one(question_to_update, updated_question)
        return schema
    
    async def get_question(self, question_id: int) -> QuestionSchema | None:
        statement = select(QuestionModel).where(QuestionModel.id == question_id)
        schema: QuestionSchema = await self.get_one(statement)
        return schema

    async def get_question_by_text(self, question_text: str) -> QuestionSchema | None:
        statement = select(QuestionModel).where(QuestionModel.question_text == question_text)
        schema: QuestionSchema = await self.get_one(statement)
        return schema

    async def get_questions(self, statement = select(QuestionModel)) -> List[QuestionSchema]:
        schemas: List[QuestionSchema] = []
        models = await self.get_all(statement)
        for model in models:
            schemas.append(QuestionSchema(**model.to_dict))
        return schemas
    
    async def get_duplicate_count_by_question_text(self) -> int:
        # Получаем количество дубликатов по question_text
        subquery = (
            select(
                QuestionModel.question_text,
                func.count(QuestionModel.id).label('count')
            )
            .group_by(QuestionModel.question_text)
            .having(func.count(QuestionModel.id) > 1)
            .subquery()
        )

        statement = select(func.sum(subquery.c.count))  # Суммируем количество дубликатов

        result = await self.session.execute(statement)
        return result.scalar() or 0  # Возвращаем общее количество дубликатов

    async def search_questions(self, q: str) -> List[QuestionSchema]:
        statement = select(QuestionModel).where(QuestionModel.question_text.ilike(f"%{q}%"))
        return await self.get_questions(statement)
