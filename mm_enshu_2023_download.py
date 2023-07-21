import os
import re
import asyncio
import json
from EdgeGPT.EdgeGPT import Chatbot, ConversationStyle

class FileHandler:
    def __init__(self, args, file_dir=None):
        if file_dir is None:
            self.file_dir = 'log/' + args.title + '/'
        self.make_dir(self.file_dir)
        
    def make_dir(self, path):
        if not os.path.exists(path):
            print('make dir: ' + path)
            os.makedirs(path)
            
    def save_to_file(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
            
    
class DialogueHandler:
    def __init__(self, args):
        # flags
        self.file_hundler = FileHandler(args=args)
        
        self.finish_asking_node = False
        self.ask_node_once = False
        self.finish_asking_edge = False
        self.ask_edge_once = False
        self.finish_asking_node_info = False
        self.ask_node_info_once = False
        self.finish_asking_node_group = False
        self.ask_node_group_once = False
        self.finish_asking_node_importance = False
        self.ask_node_importance_once = False
        
        
        # self.finish_asking_edge_info = False
        # self.ask_edge_info_once = False
        
        if args.lang == 'ja':
            self.scripts = {
                            'ask_prefix':'についての知識グラフを作成したいです．',
                            'ask_node':'知識グラフに現れるノードを出力してください.',
                            'ask_edge':'知識グラフに現れるエッジを出力してください.',
                            'ask_node_info':'ノードの情報を出力してください.',
                            'ask_node_group':'教えていただいたノードをいくつかのグループに分けてください．',
                            'ask_node_importance':'ノードの重要度を0.0から1.0の間で教えてください．',
                            'ask_tail':'以下の形式で出力してください．\n',
                            'ask_again':'指定した形式で出力しなおしてください．\n',
                            'ask_node_eg':"例'''\n- 桃太郎\n- サル\n- 犬\n'''",
                            'ask_edge_eg':"例'''\n- 桃太郎, 仲間にする, サル\n- 桃太郎, 仲間にする, 犬\n'''",
                            'ask_node_info_eg':"例'''\n- 桃太郎:桃から生まれた主人公．鬼を退治しに鬼ヶ島に向かう．\n'''",
                            'ask_node_group_eg':"例'''\n- 桃太郎:仲間\n- サル:仲間\n- 鬼:敵\n'''",
                            'ask_node_importance_eg':"例'''\n- 桃太郎:0.5\n- サル:0.5\n- 鬼:0.0\n'''",
                            }
        elif args.lang == 'en':
            self.scripts = {
                            'ask_prefix':'I want to make a knowledge graph about ',
                            'ask_node':'Please output the nodes that appear in the knowledge graph.',
                            'ask_edge':'Please output the edges that appear in the knowledge graph.',
                            'ask_node_info':'Please output the information of the node.',
                            'ask_node_group':'Please divide the nodes you taught into some groups.',
                            'ask_node_importance':'Please tell me the importance of the node between 0.0 and 1.0.',
                            'ask_tail':'Please output in the following format.\n',
                            'ask_again':'Please output again in the specified format.\n',
                            'ask_node_eg':"Example'''\n- Momotaro\n- Monkey\n- Dog\n'''",
                            'ask_edge_eg':"Example'''\n- Momotaro, make friends, Monkey\n- Momotaro, make friends, Dog\n'''",
                            'ask_node_info_eg':"Example'''\n- Momotaro: The main character born from a peach. He goes to Onigashima to defeat the demon.\n'''",
                            'ask_node_group_eg':"Example'''\n- Momotaro:Friends\n- Monkey:Friends\n- Demon:Enemy\n'''",
                            'ask_node_importance_eg':"Example'''\n- Momotaro:0.5\n- Monkey:0.5\n- Demon:0.0\n'''",
                            }
        
    def whether_Prompter_ask_node_correctly(self, output_text_from_bot):
        self.ask_node_once = True
        correct_pattern = r'^-\s(.+)$'
        ans = re.findall(correct_pattern, output_text_from_bot, re.MULTILINE)
        if ans != []:
            self.finish_asking_node = True
            path = self.file_hundler.file_dir + 'node.txt'
            self.file_hundler.save_to_file(path, output_text_from_bot)
        return ans
    
    def whether_Prompter_ask_edge_correctly(self, output_text_from_bot):
        self.ask_edge_info_once = True
        correct_pattern = r'^-\s(.+)$'
        ans = re.findall(correct_pattern, output_text_from_bot, re.MULTILINE)
        if ans:
            self.finish_asking_edge = True
            path = self.file_hundler.file_dir + 'edge.txt'
            self.file_hundler.save_to_file(path, output_text_from_bot)
        return ans
    
    def whether_Prompter_ask_node_info_correctly(self, output_text_from_bot):
        self.ask_node_info_once = True
        correct_pattern = r'^-\s(.+):(.+)$'
        ans = re.findall(correct_pattern, output_text_from_bot, re.MULTILINE)
        if ans:
            self.finish_asking_node_info = True
            path = self.file_hundler.file_dir + 'node_info.txt'
            self.file_hundler.save_to_file(path, output_text_from_bot)
        return ans
    
    def whether_Prompter_ask_node_group_correctly(self, output_text_from_bot):
        self.ask_node_group_once = True
        correct_pattern = r'^-\s(.+):(.+)$'
        ans = re.findall(correct_pattern, output_text_from_bot, re.MULTILINE)
        if ans:
            self.finish_asking_node_group = True
            path = self.file_hundler.file_dir + 'node_group.txt'
            self.file_hundler.save_to_file(path, output_text_from_bot)
        return ans
    
    def whether_Prompter_ask_node_importance_correctly(self, output_text_from_bot):
        self.ask_node_importance_once = True
        correct_pattern = r'^-\s(.+):(.+)$'
        ans = re.findall(correct_pattern, output_text_from_bot, re.MULTILINE)
        if ans:
            self.finish_asking_node_importance = True
            path = self.file_hundler.file_dir + 'node_importance.txt'
            self.file_hundler.save_to_file(path, output_text_from_bot)
        return ans
    
    # def whether_Prompter_ask_edge_info_correctly(self, output_text_from_bot):
    #     self.ask_edge_info_once = True
    #     correct_pattern
        
    
    def return_next_prompt(self, output_text_from_bot=None, title=None):
        
        # nodeについての質問作成部分
        if self.finish_asking_node == False:
            if self.ask_node_once == False: # 初めの質問
                self.ask_node_once = True
                return title + self.scripts['ask_prefix'] + self.scripts['ask_node'] + self.scripts['ask_tail'] + self.scripts['ask_node_eg']
            self.whether_Prompter_ask_node_correctly(output_text_from_bot)
            if self.ask_node_once == True and self.finish_asking_node == False: # node一覧について聞き直す
                return self.scripts['ask_again'] + self.scripts['ask_node_eg']
            
        # edgeについての質問作成部分
        if self.finish_asking_node == True and self.finish_asking_edge == False:
            if self.ask_edge_once == False: # edgeについて初めての質問
                self.ask_edge_once = True
                return title + self.scripts['ask_prefix'] + self.scripts['ask_edge'] + self.scripts['ask_tail'] + self.scripts['ask_edge_eg']
            self.whether_Prompter_ask_edge_correctly(output_text_from_bot)
            if self.ask_edge_once == True and self.finish_asking_edge == False:
                return self.scripts['ask_again'] + self.scripts['ask_edge_eg']
            
        # node_infoについての質問作成部分
        if self.finish_asking_node == True and self.finish_asking_edge == True and self.finish_asking_node_info == False:
            if self.ask_node_info_once == False:
                self.ask_node_info_once = True
                return title + self.scripts['ask_prefix'] + self.scripts['ask_node_info'] + self.scripts['ask_tail'] + self.scripts['ask_node_info_eg'] # node_infoについて初めての質問
            self.whether_Prompter_ask_node_info_correctly(output_text_from_bot)
            if self.ask_node_info_once == True and self.finish_asking_node_info == False:
                return self.scripts['ask_again'] + self.scripts['ask_node_info_eg']
            
        # node_groupについての質問作成部分
        if self.finish_asking_node == True and self.finish_asking_edge == True and self.finish_asking_node_info == True and self.finish_asking_node_group == False:
            if self.ask_node_group_once == False:
                self.ask_node_group_once = True
                return title + self.scripts['ask_prefix'] + self.scripts['ask_node_group'] + self.scripts['ask_tail'] + self.scripts['ask_node_group_eg'] # node_groupについて初めての質問
            self.whether_Prompter_ask_node_group_correctly(output_text_from_bot)
            if self.ask_node_group_once == True and self.finish_asking_node_group == False:
                return self.scripts['ask_again'] + self.scripts['ask_node_group_eg']
            
        # node_importanceについての質問作成部分
        if self.finish_asking_node == True and self.finish_asking_edge == True and self.finish_asking_node_info == True and self.finish_asking_node_group == True and self.finish_asking_node_importance == False:
            if self.ask_node_importance_once == False:
                self.ask_node_importance_once = True
                return title + self.scripts['ask_prefix'] + self.scripts['ask_node_importance'] + self.scripts['ask_tail'] + self.scripts['ask_node_importance_eg'] # node_importanceについて初めての質問
            self.whether_Prompter_ask_node_importance_correctly(output_text_from_bot)
            if self.ask_node_importance_once == True and self.finish_asking_node_importance == False:
                return self.scripts['ask_again'] + self.scripts['ask_node_importance_eg']   
            
        return 'everything is finished.'
                        
            
        
        
class ChatbotPrompter:
    def __init__(self, args):
        if args.title is None:
            self.title = input("Enter title: ")
        else:
            self.title = args.title
        
        self.dialogue_handler = DialogueHandler(args)
        
    async def main(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cookie_path = os.path.join(script_dir, 'bing_cookies_.json')
        print('cookie_path: ', cookie_path)
        cookies = json.loads(open(cookie_path, encoding="utf-8").read())
        bot = await Chatbot.create(cookies=cookies)
        
        prompt = self.dialogue_handler.return_next_prompt(title=self.title)
        response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
        print(response['text'])
        
        while True:
            prompt = self.dialogue_handler.return_next_prompt(response['text'], self.title)
            if prompt == 'everything is finished.':
                break
            response = await bot.ask(prompt=prompt, conversation_style=ConversationStyle.creative, simplify_response=True)
            print(response['text'])
        await bot.close()

if __name__ == "__main__":
    bot = ChatbotPrompter("三匹の子豚")
    asyncio.run(bot.main())