import os
import yaml
from openai import OpenAI


class CodeReviewTool:
    def __init__(self, config_path='config.yml'):
        # 加载配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.config['silicon_flow']['token'],
            base_url=self.config['silicon_flow']['base_url']
        )
        self.model = self.config['silicon_flow']['model']

    def parse_patch_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        response = ''

        segments = content.split('Index:')
        segments = [segment.strip() for segment in segments if segment.strip()]

        print(f'拆分文件判断数量:{len(segments)}')

        for index in range(1, len(segments)):
            print(f'第{index}调用api review')
            segment = segments[index]
            response += '\n' + self.call_ds_api(segment)

        return response

    def call_ds_api(self, context: str) -> str:
        prompt = """
            你是一位严格但友善的代码审查员，审查的代码是统一差异格式的代码片段，其中难免包含未实现函数、未引用方法与变量。这些都是合理存在的，我们不关注代码缺失问题。

            在你的回应中请记住下面规则：
            ```
            1. 返回的问题类型必须要在指定的类型范围内，任何情况都不得超出。
            2. 代码的格式是统一差异格式（Unified Diff Format），你只需要把删除的行忽略，只关注修改完的行。
            3. 如果用户的修改没有问题，则不返回任何内容。
            4. 不要擅自在结尾写任何形式的总结评论或概括或提要。
            5. 必须给出问题原码的范围。
            6. 返回的内容结构要清晰简明。
            ```

            你要做的是：
            1. 在每段代码中审查出中一定存在的问题，我们只关心下面这些类型的问题，不在此类型范围内的问题全部忽略。问题类型范围：
            - 逻辑错误
            - 空指针异常
            - 数组越界异常
            - 算术异常
            - 资源未关闭
            - 内存泄漏
            - 死锁
            - 线程安全问题
            - 代码重复
            - SQL注入

            2. 根据问题给出详细的原因与解决的方法，每条问题按照下面给定格式输出，其中带有<>的内容都为格式占位符：
            ### 【<问题类型>】 <简短的问题标题>
            <问题内容和建议内容>
            <问题原码和行号>
            <建议修改后的代码>
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "assistant", "content": prompt},
                {"role": "user", "content": context},
            ],
            stream=False
        )
        res = response.choices[0].message.content
        return res

    def review_code(self):
        input_dir = self.config['paths']['input_dir']
        output_dir = self.config['paths']['output_dir']

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for filename in os.listdir(input_dir):
            if filename.endswith('.txt'):
                input_filepath = os.path.join(input_dir, filename)
                output_filepath = os.path.join(output_dir, f'reviewed_{filename.replace("txt", "md")}')

                review_result = self.parse_patch_file(input_filepath)
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    f.write(review_result)
                print(f"Review completed for {filename}. Output saved to {output_filepath}")


if __name__ == '__main__':
    tool = CodeReviewTool(config_path='../config/config.yml')
    tool.review_code()
