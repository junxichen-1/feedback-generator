import os
from openai import OpenAI
from dotenv import load_dotenv

class AIFeedbackGenerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ZHIPU_API_KEY")
        self.client = None
        self._init_client()
    
    def _init_client(self):
        if self.api_key and self.api_key != "your_api_key_here":
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://open.bigmodel.cn/api/paas/v4/"
                )
            except Exception:
                self.client = None
    
    def generate_coach_feedback(self, student_name, review_num, new_num, review_forget, new_forget, is_reading=False, is_forget_training=False):
        # 防御 None 值，防止后续比较和乘法运算崩溃
        review_num = review_num if review_num is not None else 0
        new_num = new_num if new_num is not None else 0
        review_forget = review_forget if review_forget is not None else 0
        new_forget = new_forget if new_forget is not None else 0

        if not self.client:
            return self._get_default_feedback(is_reading, review_num, new_num, is_forget_training)
        
        try:
            if is_reading:
                prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。这是一节阅读理解课程。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，不要太幼稚也不要太正式
2. 先描述上课状态，比如"我们同学这节课状态不错~"、"比之前进步了"、"更集中"等
3. 夸奖孩子在阅读理解方面的表现和进步
4. 不要提及单词学习相关内容，专注于阅读理解能力的提升
5. 使用中英文短句鼓励孩子再接再厉（比如英语格言或谚语）
6. 穿插1-2个emoji表情
7. 不要太长，80-120字左右
8. 使用"我们同学"代替学生姓名
9. 语序要自然，避免"亲爱的我们同学"这种生硬的表达
"""
            elif is_forget_training:
                accuracy = int((review_num - review_forget) / review_num * 100) if review_num > 0 else 0
                prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。这是一节抗遗忘训练课程。

本节课情况：复习单词{review_num}个，遗忘{review_forget}个，正确率{accuracy}%。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，不要太幼稚也不要太正式
2. 肯定孩子认真复习的态度，鼓励孩子坚持抗遗忘训练，巩固已学单词
3. 强调复习巩固的重要性，比如"温故而知新"、"学而时习之"等
4. 使用中英文短句鼓励孩子再接再厉（比如英语格言或谚语）
5. 穿插1-2个emoji表情
6. 不要太长，80-120字左右
7. 使用"我们同学"代替学生姓名
8. 语序要自然，避免"亲爱的我们同学"这种生硬的表达
"""
            else:
                if new_num == 0:
                    prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。

本节课情况：没有新学单词，主要复习已学内容。复习单词：{review_num}个，遗忘{review_forget}个。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，不要太幼稚也不要太正式
2. 肯定孩子认真复习的态度，鼓励孩子先掌握已学单词、夯实基础再学新内容
3. 强调基础的重要性，比如"万丈高楼平地起"、"打好基础才能飞得更高"等
4. 使用中英文短句鼓励孩子再接再厉（比如英语格言或谚语）
5. 穿插1-2个emoji表情
6. 不要太长，80-120字左右
7. 使用"我们同学"代替学生姓名
8. 语序要自然，避免"亲爱的我们同学"这种生硬的表达
"""
                elif review_num == 0:
                    prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。

本节课情况：没有复习单词，全部是新学内容。新学单词：{new_num}个，遗忘{new_forget}个。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，不要太幼稚也不要太正式
2. 夸奖孩子接受新知识的能力，鼓励孩子本节课新单词任务量大，提醒注意已有单词的巩固
3. 建议孩子在学习新单词的同时，也要定期复习之前学过的内容，温故而知新
4. 使用中英文短句鼓励孩子再接再厉（比如英语格言或谚语）
5. 穿插1-2个emoji表情
6. 不要太长，80-120字左右
7. 使用"我们同学"代替学生姓名
8. 语序要自然，避免"亲爱的我们同学"这种生硬的表达
"""
                else:
                    prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。请根据以下数据：
- 复习单词：{review_num}个，遗忘{review_forget}个
- 新学单词：{new_num}个，遗忘{new_forget}个

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，不要太幼稚也不要太正式
2. 先描述上课状态，比如"我们同学这节课状态不错~"、"比之前进步了"、"更集中"等
3. 夸奖孩子用功努力
4. 使用中英文短句鼓励孩子再接再厉（比如英语格言或谚语）
5. 穿插1-2个emoji表情
6. 不要太长，80-120字左右
7. 使用"我们同学"代替学生姓名
8. 语序要自然，避免"亲爱的我们同学"这种生硬的表达
"""
            
            response = self.client.chat.completions.create(
                model="chatglm_turbo",
                messages=[
                    {"role": "system", "content": "你是一位亲切、专业的英语陪练老师，擅长用鼓励的方式激励学生。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"AI生成反馈失败: {str(e)}")
            return self._get_default_feedback(is_reading, review_num, new_num, is_forget_training)
    
    def _get_default_feedback(self, is_reading=False, review_num=0, new_num=0, is_forget_training=False):
        if is_reading:
            return "这节课我们同学在阅读理解方面表现不错~文章理解能力有明显提升，答题思路也更加清晰了。坚持每天阅读，你的英语综合能力会越来越强！Reading makes a full man，继续加油！📚"
        elif is_forget_training:
            return "这节课我们同学坚持抗遗忘训练，态度非常认真~复习了不少已学单词，遗忘率控制得不错！温故而知新，坚持定期复习才能让知识更牢固。记住\"Repetition is the mother of learning\"，继续保持！🔄"
        else:
            if new_num == 0:
                return "这节课我们同学专注于复习已学单词，态度非常认真~万丈高楼平地起，先把基础打扎实才能飞得更高。相信自己，每一次复习都是在为未来的进步铺路！Practice makes perfect，继续保持！📖"
            elif review_num == 0:
                return "这节课我们同学学习了不少新单词，接受能力很棒！不过新单词任务量大，别忘了定期复习之前学过的内容哦~温故而知新，可以为师矣。学习新内容的同时也要巩固旧知识，加油！💪"
            else:
                return "这节课我们同学基本跟上了节奏，大部分知识点都能理解，偶尔在细节上需要再巩固一下。别担心，每一次认真听课都是进步的开始。记住\"Rome wasn't built in a day\"，坚持积累，你一定能突破瓶颈，加油！💪"

if __name__ == "__main__":
    generator = AIFeedbackGenerator()
    
    print("===== 场景1：无新单词（只有复习） =====")
    feedback1 = generator.generate_coach_feedback("学生姓名", review_num=20, new_num=0, review_forget=3, new_forget=0, is_reading=False)
    print(feedback1)
    print()
    
    print("===== 场景2：无复习单词（只有新学） =====")
    feedback2 = generator.generate_coach_feedback("学生姓名", review_num=0, new_num=30, review_forget=0, new_forget=5, is_reading=False)
    print(feedback2)
    print()
    
    print("===== 场景3：既有复习又有新学（正常情况） =====")
    feedback3 = generator.generate_coach_feedback("学生姓名", review_num=15, new_num=10, review_forget=2, new_forget=1, is_reading=False)
    print(feedback3)
    print()
    
    print("===== 场景4：抗遗忘训练课程 =====")
    feedback4 = generator.generate_coach_feedback("学生姓名", review_num=68, new_num=0, review_forget=2, new_forget=0, is_reading=False, is_forget_training=True)
    print(feedback4)