import yaml
from os import rename, path, makedirs
from datetime import datetime
import random


class main:
    def __init__(self):
        # Logo
        print("""
        ╭━━━╮     ╭╮          ╭╮╭╮
        ┃╭━╮┃     ┃┃          ┃┣╯╰╮
        ┃┃ ╰╋━━┳╮╭┫╰━┳━━╮╭━━┳━╯┣╮╭╋━━┳━╮
        ┃┃ ╭┫╭╮┃╰╯┃╭╮┃╭╮┃┃┃━┫╭╮┣┫┃┃╭╮┃╭╯
        ┃╰━╯┃╰╯┃┃┃┃╰╯┃╰╯┃┃┃━┫╰╯┃┃╰┫╰╯┃┃
        ╰━━━┻━━┻┻┻┻━━┻━━╯╰━━┻━━┻┻━┻━━┻╯
                           By SniFo\n""")
        # ------------------------> Load config.yml <------------------------
        try:
            with open("Config.yml", encoding="utf-8") as file:
                config = yaml.full_load(file)['main']
                # ------------------------> Read <------------------------
                self.read_character = str(config['Read']['character'])
                self.read_position = int(config['Read']['position'])
                self.read_encode = str(config['Read']['encode'])
                # ------------------------> Text <------------------------
                self.duplicates = bool(config['Duplicates'])
                self.reverse = bool(config['Reverse'])
                # ------------------------> Length <------------------------
                self.length_enable = bool(config['Length']['enable'])
                self.length_minimum = int(config['Length']['minimum'])
                # ------------------------> Password <------------------------
                self.edit_enable = bool(config['Edit']['enable'])
                self.edit_title = bool(config['Edit']['title'])
                self.edit_chance = int(config['Edit']['chance'])
                self.edit_password = str(config['Edit']['password'])
                self.edit_keywords = list(config['Edit']['keywords'])
                # ------------------------> Whitelist <------------------------
                self.whitelist_enable = bool(config['Whitelist']['enable'])
                self.whitelist_keywords = list(config['Whitelist']['keywords'])
                # ------------------------> Blacklist <------------------------
                self.blacklist_enable = bool(config['Blacklist']['enable'])
                self.blacklist_keywords = list(config['Blacklist']['keywords'])
                file.close()
        except Exception as Error:
            print(f"| Error | Loading config at", Error)
            exit()
        # ------------------------> Checking values <------------------------
        if self.read_position < 0:
            print(f"| Config | Position has to be higher or equal to 0")
            exit()
        elif not 100 >= self.edit_chance >= 0:
            print(f"| Config | Chance has to be higher or equal to 0")
            exit()
        # ------------------------> Creating latest.txt <------------------------
        # Loading file
        if path.exists("Output/latest.txt"):
            temp: int = 1
            while True:
                old_path = f"Output/{datetime.now().date()}-{temp}.txt"
                if not path.exists(old_path):
                    rename("Output/latest.txt", str(old_path))
                    break
                else:
                    temp += 1
        else:
            if not path.exists("Output"):
                makedirs(f"Output")
        # ------------------------> Loading combo <------------------------
        with open("Combo.txt", 'r', encoding="utf-8", errors='ignore') as file:
            self.combo: list = [line.strip() for line in file.readlines()]
            file.close()
        print(f"| Input |", len(self.combo), "line(s)")
        # ------------------------> Start filtering <------------------------
        temp_list: list = list()
        if self.duplicates:
            old = len(self.combo)
            self.combo = list(dict.fromkeys(self.combo))
            print(f"| Duplicates |", old - len(self.combo), "lines has been removed")
        if self.reverse:
            self.combo.reverse()
            print(f"| Reverse | Done")
        for line in self.combo:
            if account := self.read(line):
                # ------------------------> Whitelist & Blacklist <------------------------
                if self.whitelist_enable or self.blacklist_enable:
                    if self.whitelist_enable:
                        if [x for x in self.whitelist_keywords if x in account]:
                            temp_list.append(account)
                    elif self.blacklist_enable:
                        if not [x for x in self.blacklist_keywords if x in account]:
                            temp_list.append(account)
                else:
                    temp_list.append(account)
        if self.whitelist_enable or self.blacklist_enable:
            print(f"| Whitelist & Blacklist |", len(self.combo) - len(temp_list), "lines has been removed")
        # ------------------------> Length <------------------------
        final_list: list = list()
        if self.length_enable:
            for account in temp_list:
                first = str(account).split(self.read_character)[0]
                last = str(account).split(self.read_character)[-1]
                if not (0 < self.length_minimum <= len(last)):
                    temp_list.remove(account)
                else:
                    # ------------------------> Edit <------------------------
                    if random.randint(0, 100) <= self.edit_chance:
                        if self.edit_title:
                            last = last.title()
                        if not [x for x in self.edit_keywords if x in last]:
                            last = self.edit_password.replace("{pass}", last)
                        final_list.append(first + self.read_character + last)
                    else:
                        final_list.append(account)
        if self.length_enable:
            print(f"| Length |", len(temp_list) - len(final_list), "lines has been removed")
        temp_list.clear()
        print(f"| Output |", len(final_list), "line(s)")
        with open("Output/latest.txt", "a") as file:
            file.writelines("%s\n" % item for item in final_list)
            file.close()

    def read(self, line: str) -> str or bool:
        account = str()
        n = 0
        for i in line.split(" "):
            if self.read_character in i:
                n += 1
                if n == self.read_position or n >= line.count(":"):
                    account = i
                    try:
                        i.encode(self.read_encode)
                    except Exception as error:
                        if not type(error) == UnicodeEncodeError:
                            print(f"| Error |", str(error).title())
                            exit()
                        n = 0
                    break
        if n == 0:
            return False
        else:
            return account


main()
