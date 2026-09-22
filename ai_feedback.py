import os
import random
from openai import OpenAI
from dotenv import load_dotenv

# 课堂表现细节片段池，供兜底模板随机引用，让每次反馈更鲜活
CLASS_DETAILS = [
    "状态很在线", "表现得不错", "整节课都很投入", "课堂状态比之前稳定多了",
    "能看出在认真跟着老师的节奏走", "听得很专注", "愿意沉下心来学",
    "有主动开口跟读", "有努力纠正自己的发音", "回答问题很积极",
    "遇到难点没有退缩，慢慢在琢磨", "记笔记很认真", "跟读单词时声音很清晰",
]

# 鼓励用的英文短句池
ENCOURAGE_EN = [
    "Practice makes perfect", "Rome wasn't built in a day",
    "Repetition is the mother of learning", "Little by little, one travels far",
    "Every cloud has a silver lining", "Believe you can and you're halfway there",
]

# 中文俗语/金句池
CHINESE_PROVERBS = [
    "温故而知新", "万丈高楼平地起", "学而时习之，不亦说乎",
    "不积跬步，无以至千里", "一分耕耘一分收获", "千里之行，始于足下",
]

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
            return self._get_default_feedback(is_reading, review_num, new_num, review_forget, new_forget, is_forget_training)
        
        try:
            if is_reading:
                prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。这是一节阅读理解课程。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，口语化，像老师私下和孩子聊天，不要太幼稚也不要太正式
2. 先点出上课状态，可从以下角度任选1-2个来写（不要每次都用同一种说法）：课堂专注、主动思考、愿意沉下心读、回答问题积极、跟着老师节奏、敢于表达想法
3. 夸奖孩子在阅读理解方面的表现和进步（比如文章理解更到位、答题思路更清晰、定位信息更快等）
4. 不要提及单词学习相关内容，专注于阅读理解能力的提升
5. 结尾用一句中英文短句鼓励（英文格言/谚语或中文俗语均可，每次换一句）
6. 穿插1个emoji表情即可
7. 80-120字左右
8. 使用"我们同学"代替学生姓名，不要写"亲爱的我们同学"这种生硬称呼
9. 换着花样写，不要每次都用"这节课我们同学..."开头，也不要重复相同句式
"""
            elif is_forget_training:
                accuracy = int((review_num - review_forget) / review_num * 100) if review_num > 0 else 0
                prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。这是一节抗遗忘训练课程。

本节课情况：复习单词{review_num}个，遗忘{review_forget}个，正确率{accuracy}%。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，口语化
2. 肯定孩子认真复习的态度，可从以下角度任选1-2个：坚持复习不偷懒、遗忘率在下降、愿意反复跟读、越错越勇、沉下心巩固
3. 强调复习巩固的重要性，引用一句俗语（如"温故而知新"、"学而时习之"、"不积跬步无以至千里"等，每次换一句）
4. 结尾用一句英文格言鼓励（每次换一句）
5. 穿插1个emoji表情即可
6. 80-120字左右
7. 使用"我们同学"代替学生姓名，不要生硬称呼
8. 换着花样写，不要每次都用相同开头和句式
"""
            else:
                if new_num == 0:
                    prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。

本节课情况：没有新学单词，主要复习已学内容。复习单词：{review_num}个，遗忘{review_forget}个。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，口语化
2. 肯定孩子认真复习的态度，可从以下角度任选1-2个：愿意沉下心复习、跟读很认真、有努力纠正发音、记笔记仔细、不骄不躁
3. 鼓励先把已学单词夯实再学新内容，引用一句关于"基础"的俗语（如"万丈高楼平地起"、"千里之行始于足下"等，每次换一句）
4. 结尾用一句英文格言鼓励（每次换一句）
5. 穿插1个emoji表情即可
6. 80-120字左右
7. 使用"我们同学"代替学生姓名，不要生硬称呼
8. 换着花样写，不要每次都用相同开头和句式
"""
                elif review_num == 0:
                    prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。

本节课情况：没有复习单词，全部是新学内容。新学单词：{new_num}个，遗忘{new_forget}个。

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，口语化
2. 夸奖孩子接受新知识的能力，可从以下角度任选1-2个：接受新单词很快、敢于开口读、有努力纠正发音、课堂跟着老师走、学习劲头足
3. 提醒孩子新单词任务量大，别忘了定期复习之前学过的内容（温故而知新）
4. 结尾用一句英文格言鼓励（每次换一句）
5. 穿插1个emoji表情即可
6. 80-120字左右
7. 使用"我们同学"代替学生姓名，不要生硬称呼
8. 换着花样写，不要每次都用相同开头和句式
"""
                else:
                    prompt = f"""你是一位专业的英语陪练老师，正在给初中学生{student_name}写课后反馈。请根据以下数据：
- 复习单词：{review_num}个，遗忘{review_forget}个
- 新学单词：{new_num}个，遗忘{new_forget}个

请写一段温馨、鼓励性的陪练反馈，要求：
1. 面向初中学生，语气亲切自然，口语化
2. 先点出上课状态，可从以下角度任选1-2个来写（不要每次都用同一种说法）：这节课表现不错、有努力纠正发音、愿意沉下心学习、课堂状态很在线、回答问题积极、跟着老师节奏、记笔记认真
3. 夸奖孩子用功努力，并结合上面的单词数据给一句具体肯定（比如"复习了{review_num}个单词，遗忘才{review_forget}个，记得很牢"这类，随机换说法）
4. 结尾用一句英文格言或中文俗语鼓励（每次换一句）
5. 穿插1个emoji表情即可
6. 80-120字左右
7. 使用"我们同学"代替学生姓名，不要写"亲爱的我们同学"这种生硬称呼
8. 换着花样写，不要每次都用"这节课我们同学基本跟上了节奏"这类固定句式，开头也要换
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
            return self._get_default_feedback(is_reading, review_num, new_num, review_forget, new_forget, is_forget_training)
    
    def _get_default_feedback(self, is_reading=False, review_num=0, new_num=0, review_forget=0, new_forget=0, is_forget_training=False):
        """AI不可用时的兜底反馈：每个场景多个模板随机选择，并随机组合课堂细节、俗语、英文格言，避免千篇一律。"""
        detail = random.choice(CLASS_DETAILS)
        en = random.choice(ENCOURAGE_EN)
        prov = random.choice(CHINESE_PROVERBS)

        if is_reading:
            templates = [
                f"{detail}~阅读理解做得越来越顺手了，文章大意抓得准，答题思路也比之前清晰。坚持每天读一点，英语综合能力会稳步提升。{en}，继续加油！📚",
                f"我们同学这节课{random.choice(['沉下心读了','跟着老师思路走了','主动思考了'])}，对文章的理解更到位了，定位信息也快了不少。阅读就是这样，读得多了自然就有语感。{en}，保持下去！📖",
                f"这节课阅读状态不错，能看出我们同学在认真琢磨文章意思，答题时也更有把握了。每天坚持阅读，收获会越来越明显。{en}，加油！📚",
            ]
            return random.choice(templates)

        if is_forget_training:
            templates = [
                f"我们同学{detail}，复习了{review_num}个单词，遗忘才{review_forget}个，记得很牢！{prov}，定期复习才能把知识焊在脑子里。{en}，继续保持！🔄",
                f"这节课抗遗忘训练我们同学很认真，{random.choice(['越错越勇','沉下心反复跟读','不偷懒'])}，正确率稳中有升。{prov}，坚持复习就是最好的记忆方法。{en}，加油！📖",
                f"抗遗忘训练贵在坚持，我们同学这节课{detail}，{review_num}个单词只忘了{review_forget}个，表现可圈可点。{prov}，继续巩固，你会越来越棒！🔄",
            ]
            return random.choice(templates)

        if new_num == 0:
            templates = [
                f"我们同学{detail}，这节课专注复习已学单词，{review_num}个单词只忘了{review_forget}个，基础打得很稳。{prov}，先把地基打牢才能建高楼。{en}，继续保持！📖",
                f"这节课主要是复习，我们同学{random.choice(['跟读很认真','有努力纠正发音','记笔记很仔细'])}，{review_num}个单词遗忘{review_forget}个，掌握得不错。{prov}，夯实基础比赶进度更重要。{en}，加油！💪",
                f"复习课我们同学{detail}，{review_num}个单词只错了{review_forget}个，态度很踏实。{prov}，把已学的吃透了，学新内容才更轻松。{en}，继续！📖",
            ]
            return random.choice(templates)

        if review_num == 0:
            templates = [
                f"我们同学{detail}，这节课学了{new_num}个新单词，遗忘{new_forget}个，接受能力很棒！不过新内容多，记得回头复习旧知识哦~{prov}。{en}，加油！💪",
                f"这节课全是新单词，我们同学{random.choice(['敢于开口读','有努力纠正发音','跟着老师节奏'])}，{new_num}个单词只忘了{new_forget}个，学得很快。学新别忘了温故，{prov}。{en}，继续！📚",
                f"新单词任务量不小，我们同学{detail}，{new_num}个新词遗忘{new_forget}个，表现超出预期。记得抽时间复习之前学过的，{prov}。{en}，保持劲头！💪",
            ]
            return random.choice(templates)

        # 既有复习又有新学（最常见场景）
        templates = [
            f"我们同学{detail}，这节课复习{review_num}个、新学{new_num}个单词，遗忘分别是{review_forget}和{new_forget}个，整体掌握得不错。{prov}，继续积累！{en}，加油！💪",
            f"{detail}，复习的{review_num}个单词只忘了{review_forget}个，新学的{new_num}个也消化得挺好。能看出在认真学，继续保持这份劲头。{en}，你可以的！📖",
            f"这节课我们同学{random.choice(['状态很在线','表现得不错','愿意沉下心学'])}，复习{review_num}个遗忘{review_forget}个，新学{new_num}个遗忘{new_forget}个，节奏拿捏得不错。{prov}，日积月累会有大进步！{en}，加油！💪",
            f"能感觉到我们同学这节课{detail}，{review_num}个复习单词错得不多，{new_num}个新单词也跟上了。每一步认真都算数。{en}，继续向前！📚",
            f"我们同学{random.choice(['有努力纠正自己的发音','回答问题很积极','记笔记很认真'])}，复习{review_num}个、新学{new_num}个单词，遗忘率都控制得不错。{prov}，坚持下去进步会越来越明显！{en}，加油！💪",
        ]
        return random.choice(templates)

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
