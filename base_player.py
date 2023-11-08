'''
base_player.py
Copyright (C) 2023 Kentaroh Nonaka

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

This program is based on the base_player.py part of <https://github.com/TadaoYamaoka/python-dlshogi2/tree/main/pydlshogi2/player> by Tadao Yamaoka.
The original work is licensed under the GNU General Public License version 3.
This program has been modified by Kentaroh Nonaka on 2023-01.
'''

import time
from concurrent.futures import ThreadPoolExecutor

class BasePlayer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None

    def usi(self):
        pass

    def usinewgame(self):
        pass

    def setoption(self, args):
        pass

    def isready(self):
        pass

    def position(self, sfen, usi_moves):
        pass

    def set_limits(self, btime=None, wtime=None, byoyomi=None, binc=None, winc=None, nodes=None, infinite=False, ponder=False):
        pass

    def go(self):
        pass

    def stop(self):
        pass

    def ponderhit(self, last_limits):
        pass

    def quit(self):
        pass

    def run(self):
        while True:
            cmd_line = input().strip()
            cmd = cmd_line.split(' ', 1)

            if cmd[0] == 'usi':
                self.usi()
                print('usiok', flush=True)
            elif cmd[0] == 'setoption':
                option = cmd[1].split(' ')
                self.setoption(option)
            elif cmd[0] == 'isready':
                self.isready()
                print('readyok', flush=True)
            elif cmd[0] == 'usinewgame':
                self.usinewgame()
            elif cmd[0] == 'position':
                args = cmd[1].split('moves')
                self.position(args[0].strip(), args[1].split() if len(args) > 1 else [])
            elif cmd[0] == 'go':
                kwargs = {}
                if len(cmd) > 1:
                    args = cmd[1].split(' ')
                    if args[0] == 'infinite':
                        kwargs['infinite'] = True
                    else:
                        if args[0] == 'ponder':
                            kwargs['ponder'] = True
                            args = args[1:]
                        for i in range(0, len(args) - 1, 2):
                            if args[i] in ['btime', 'wtime', 'byoyomi', 'binc', 'winc', 'nodes']:
                                kwargs[args[i]] = int(args[i + 1])
                #秒読み時間を10秒で固定するように変更
                self.set_limits(byoyomi=10000)
                # ponderhitのために条件と経過時間を保存
                last_limits = kwargs
                need_print_bestmove = 'ponder' not in kwargs and 'infinite' not in kwargs

                def go_and_print_bestmove():
                    bestmove, ponder_move = self.go()
                    if need_print_bestmove:
                        print('bestmove ' + bestmove + (' ponder ' + ponder_move if ponder_move else ''), flush=True)
                    return bestmove, ponder_move
                self.future = self.executor.submit(go_and_print_bestmove)
            elif cmd[0] == 'stop':
                need_print_bestmove = False
                self.stop()
                bestmove, _ = self.future.result()
                print('bestmove ' + bestmove, flush=True)
            elif cmd[0] == 'ponderhit':
                last_limits['ponder'] = False
                self.ponderhit(last_limits)
                bestmove, ponder_move = self.future.result()
                print('bestmove ' + bestmove + (' ponder ' + ponder_move if ponder_move else ''), flush=True)
            elif cmd[0] == 'quit':
                self.quit()
                break
