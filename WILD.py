import random
import time
import os

class GameState:
    def __init__(self):
        self.hp = 22
        self.max_hp = 30
        self.day = 1
        self.alive = True
        self.escaped = False
        self.water = 6
        self.food = 5
        self.location = 0
        self.location_names = ["🏖️ 沙滩", "🌿 中部灌木丛", "🌳 中心树林"]
        self.period = 0
        self.period_names = ["🌅 清晨", "☀️ 白天", "🌆 傍晚", "🌙 夜晚"]
        self.actions_today = 0
        self.max_actions = 10
        self.wood = 0
        self.driftwood = 1   # ★ 改动1：开局赠送一根漂流木
        self.stone = 0
        self.vine = 0
        self.flint = 0
        self.fish_count = 0
        self.fruit = 0
        self.herb = 0
        self.shells = 0
        self.hide = 0
        self.bone = 0
        self.coconut = 0
        self.water_units = 0
        self.has_shelter = False
        self.has_fire = False
        self.has_stone_axe = False
        self.has_stone_knife = False
        self.has_fishing_rod = False
        self.raft_progress = 0
        self.raft_built = False
        self.raft_stored_safely = False
        self.found_wreck = False
        self.found_stone = False
        self.found_bottle = False
        self.explored_center = False
        self.has_direction = False
        self.storm_day = None
        self.storm_triggered = False
        self.storm_active = False
        self.storm_duration = 0
        self.has_weapon = False
        self.weapon_type = "拳头"
        self.discovered_raft_need = False
        self.camp_water = 0

    def show_status(self):
        print("\n" + "="*50)
        print(f"🏝️ 荒岛生存 · 第 {self.day} 天 · {self.period_names[self.period]}")
        print("="*50)
        hp_bar = "█" * int((self.hp / self.max_hp) * 10) + "░" * (10 - int((self.hp / self.max_hp) * 10))
        print(f"❤️ HP: {self.hp}/{self.max_hp} [{hp_bar}]")
        print(f"💧 水分: {self.water}/10  |  🍖 饱食: {self.food}/10")
        print(f"📍 位置: {self.location_names[self.location]}")
        print(f"⏳ 今日行动: {self.actions_today}/{self.max_actions}")
        print("-"*50)
        print(f"🪵 木材:{self.wood}  🪨 石头:{self.stone}  🌿 藤蔓:{self.vine}")
        print(f"💧 淡水储备:{self.water_units}  🐟 鱼:{self.fish_count}  🍎 野果:{self.fruit}")
        print(f"🌿 药草:{self.herb}  🔥 燧石:{self.flint}  🥥 椰子壳:{self.coconut}")
        print(f"🏖️ 漂流木:{self.driftwood}  🐚 贝壳:{self.shells}")
        print("-"*50)
        shelter_status = "✅" if self.has_shelter else "❌"
        fire_status = "✅" if self.has_fire else "❌"
        axe_status = "✅" if self.has_stone_axe else "❌"
        knife_status = "✅" if self.has_stone_knife else "❌"
        rod_status = "✅" if self.has_fishing_rod else "❌"
        raft_pct = int((self.raft_progress / 30) * 100) if self.raft_progress > 0 else 0
        raft_status = f"{raft_pct}%" if not self.raft_built else "✅ 已造好"
        print(f"🏕️ 庇护所:{shelter_status}  🔥 火堆:{fire_status}  🪓 石斧:{axe_status}")
        print(f"🔪 石刀:{knife_status}  🎣 鱼竿:{rod_status}  ⛵ 木筏:{raft_status}")
        if self.raft_built and not self.raft_stored_safely:
            print("   ⚠️ 木筏放在沙滩上，暴风雨可能冲走！")
        elif self.raft_built and self.raft_stored_safely:
            print("   ✅ 木筏已拖到安全位置。")
        if self.storm_day is not None and not self.storm_triggered:
            days_left = self.storm_day - self.day
            if days_left > 0:
                print(f"   ⛈️ 你感觉风暴将在 {days_left} 天后到来……")
        elif self.storm_active:
            print("   ⛈️⛈️ 暴风雨正在肆虐！⛈️⛈️")
        print("="*50)

    def show_actions(self):
        print("\n📋 行动指令:")
        print("  【移动】")
        print("    m1  前往沙滩    m2  前往中部灌木丛    m3  前往中心树林（需先经过灌木丛）")
        print("  【采集】")
        print("    cw  采集木材    cs  采集石头    cv  采集藤蔓")
        print("    cwater  采集淡水    cflint  采集燧石（需石斧）")
    print("    carrywater  用椰子壳携带淡水回庇护所（需椰子壳，每次2份）")
        print("    pick  沙滩拾取（漂流木/贝壳）")
        print("  【食物】")
        print("    fish  钓鱼（需鱼竿）    hunt  狩猎（战斗）")
        print("    gather  中部采集（野果/药草/藤蔓/可能中毒）")
        print("  【建造】")
        print("    build  打开建造菜单")
        print("  【其他】")
        print("    explore  探索当前区域    rest  休息（恢复HP）")
        print("    eat  食用食物    drink  饮用淡水    herb  使用药草")
        print("    raft  检查木筏状态    store  将木筏拖到安全位置")
        print("  【离开】")
        print("    leave  尝试离开荒岛")
        print("  【时间】")
        print("    night  结束今天")
        print("  【状态】")
        print("    status  查看状态    help  显示此菜单")

    def move_to(self, target):
        if target == self.location:
            print(f"📍 你已经在 {self.location_names[target]} 了。")
            return
        if target == 2 and self.location == 0:
            # ★ 改动2：提示玩家还需要再走一步
            print("🌿 你穿过中部灌木丛，向中心树林前进……")
            self.location = 1
            print(f"📍 你现在在 {self.location_names[1]}，再输入 m3 可继续前往中心树林。")
            self.actions_today += 0.5
            return
        self.location = target
        print(f"📍 你来到了 {self.location_names[target]}")
        self.actions_today += 0.5
        if target == 2 and not self.explored_center:
            self.explored_center = True
            print("\n🌳 你看到一片茂密的树林，树下散落着石块和燧石。")
            print("   💡 这里可以采集木材、石头和燧石。远处似乎还有泉水的声音。")

    def collect_wood(self):
        if self.location != 2:
            print("🌳 这里没有足够的树木。你需要到中心树林去砍树。")
            return
        if not self.has_stone_axe:
            print("🪓 你需要一把石斧才能砍树。")
            print("   💡 去采集石头，再捡点漂流木，先造一把石斧吧。")
            return
        self.hp -= 3
        self.food -= 1
        self.water -= 1
        self.actions_today += 1
        amount = random.randint(2, 4)
        self.wood += amount
        print(f"🪵 你砍了一些树木，获得 {amount} 份木材（当前: {self.wood}）")
        if not self.discovered_raft_need and self.wood >= 10:
            self.discovered_raft_need = True
            print("💡 你看着堆起来的木头，心想：也许能造点什么离开这里……")
        self.check_vitals()

    def collect_stone(self):
        if self.location != 2:
            print("这里没有石头。你需要到中心树林去采集。")
            return
        self.hp -= 2
        self.food -= 1
        self.water -= 1
        self.actions_today += 1
        amount = random.randint(4, 5)
        self.stone += amount
        print(f"🪨 你采集了 {amount} 块石头（当前: {self.stone}）")
        self.check_vitals()

    def collect_vine(self):
        if self.location != 1:
            print("🌿 这里没有藤蔓。你需要到中部灌木丛去采集。")
            return
        self.hp -= 2
        self.food -= 1
        self.water -= 1
        self.actions_today += 1
        amount = 3
        self.vine += amount
        print(f"🌿 你采集了 {amount} 根藤蔓（当前: {self.vine}）")
        self.check_vitals()

    def collect_water(self):
        if self.location != 2:
            print("💧 只有中心树林的泉水可以采集淡水。")
            return
        self.actions_today += 1
        amount = 3
        self.water_units += amount
        self.water = 10
        print(f"💧 你从泉水处采集了 {amount} 份淡水（储备: {self.water_units}，当前水分: {self.water}/10）")

    def carry_water(self):
        if self.location != 2:
            print("💧 只有中心泉水处可以用椰子壳盛水。")
            return
        if self.coconut < 1:
            print("🥥 你没有椰子壳，无法携带淡水。")
            return
        self.water_units += 2
        self.water = 10
        print(f"🥥 你用椰子壳盛了 2 份淡水（储备: {self.water_units}，当前水分: {self.water}/10）")

    def collect_flint(self):
        if self.location != 2:
            print("这里没有燧石。你需要到中心树林去找。")
            return
        if not self.has_stone_axe:
            print("🪓 你需要石斧才能敲下燧石。")
            return
        self.actions_today += 1
        amount = random.randint(3, 4)
        self.flint += amount
        print(f"🔥 你采集了 {amount} 块燧石（当前: {self.flint}）")

    def pick_beach(self):
        if self.location != 0:
            print("🏖️ 只有沙滩上可以拾取。")
            return
        self.actions_today += 1
        roll = random.random()
        if roll < 0.6:
            amount = random.randint(1, 2)
            self.driftwood += amount
            print(f"🪵 你捡到了 {amount} 段漂流木（当前: {self.driftwood}）")
        else:
            amount = random.randint(1, 5)
            self.shells += amount
            print(f"🐚 你捡到了 {amount} 个贝壳（当前: {self.shells}）")
        if not self.found_bottle and random.random() < 0.1:
            self.found_bottle = True
            print("\n🧴 你发现了一个漂流瓶！里面有张字条：")
            print("   '向西航行……你会找到一个叫迷雾港的地方。'")
            self.has_direction = True

    def gather_middle(self):
        if self.location != 1:
            print("🌿 你需要到中部灌木丛去采集。")
            return
        self.hp -= 2
        self.food -= 1
        self.water -= 1
        self.actions_today += 1
        roll = random.random()
        if roll < 0.55:
            amount = random.randint(3, 5)
            self.fruit += amount
            self.water = min(10, self.water + 1)
            print(f"🍎 你发现了 {amount} 个野果！（当前: {self.fruit}）")
        elif roll < 0.75:
            self.herb += 1
            print(f"🌿 你找到了一株药草！（当前: {self.herb}）")
            print("   💡 药草可以治疗 +4HP，输入 herb 使用。")
        elif roll < 0.90:
            amount = random.randint(2, 3)
            self.vine += amount
            print(f"🌿 你割下了 {amount} 根藤蔓！（当前: {self.vine}）")
        else:
            self.hp -= 5
            print("🍄 你误食了毒蘑菇！-5 HP")
        self.check_vitals()

    def go_fish(self):
        if self.location != 0:
            print("🎣 钓鱼需要在沙滩海边。")
            return
        if not self.has_fishing_rod:
            print("🎣 你还没有鱼竿。需要木材和藤蔓制作。")
            return
        self.actions_today += 1
        success_rate = 0.7
        if self.period == 0:
            success_rate = 0.85
        elif self.period == 3:
            success_rate = 0.5
        if random.random() < success_rate:
            amount = random.randint(1, 2)
            self.fish_count += amount
            print(f"🐟 你钓到了 {amount} 条鱼！（当前: {self.fish_count}）")
        else:
            print("🐟 今天鱼儿不太活跃，什么都没钓到。")

    def hunt(self):
        if self.location == 0:
            print("沙滩上没有野兽。你需要到中部或中心区域狩猎。")
            return
        self.actions_today += 1
        prey_data = [
            ("野猪", 15, 4, 2),
            ("巨鸟", 10, 3, 1),
            ("毒蛇", 7, 5, 0),
        ]
        name, hp, atk, defense = random.choice(prey_data)
        print(f"\n⚔️ 你遇到了 {name}！")
        print(f"   HP: {hp} | 攻击: {atk}")
        player_atk = 3
        if self.has_stone_knife:
            player_atk = 6
        elif self.has_stone_axe:
            player_atk = 5
        while hp > 0 and self.hp > 0:
            damage = max(1, player_atk + random.randint(-1, 2) - defense)
            hp -= damage
            print(f"   💥 你造成 {damage} 点伤害！（{name} HP: {hp}）")
            if hp <= 0:
                print(f"   ✅ 击败了 {name}！")
                self.hide += 1
                self.bone += 1
                self.food = min(10, self.food + 2)
                self.hp -= 2
                print(f"   🥩 获得兽皮 x1, 骨头 x1, 饱食 +2")
                self.check_vitals()
                return
            enemy_damage = max(1, atk + random.randint(0, 2) - 1)
            self.hp -= enemy_damage
            print(f"   💢 {name} 反击，造成 {enemy_damage} 点伤害！（你的 HP: {self.hp}）")
            if self.hp <= 0:
                print("💀 你被野兽击败了……")
                self.alive = False
                return

    def build_menu(self):
        print("\n" + "="*40)
        print("🛠️ 建造菜单")
        print("="*40)
        print(f"当前材料: 木材{self.wood} | 漂流木{self.driftwood} | 石头{self.stone} | 藤蔓{self.vine} | 燧石{self.flint}")
        print("-"*40)
        projects = []
        if not self.has_shelter:
            missing = []
            if self.vine < 2: missing.append(f"藤蔓x{2-self.vine}")
            if self.wood + self.driftwood < 5: missing.append(f"木材/漂流木x{5-(self.wood+self.driftwood)}")
            if missing: projects.append(("🏕️ 庇护所", "❌ 缺少: " + ", ".join(missing), False))
            else: projects.append(("🏕️ 庇护所", "▶️ [1] 建造（藤蔓x2 + 木材/漂流木x5）", True))
        if not self.has_fire:
            missing = []
            if self.flint < 3: missing.append(f"燧石x{3-self.flint}")
            if self.wood + self.driftwood < 2: missing.append(f"木材/漂流木x{2-(self.wood+self.driftwood)}")
            if missing: projects.append(("🔥 火堆", "❌ 缺少: " + ", ".join(missing), False))
            else: projects.append(("🔥 火堆", "▶️ [2] 建造（燧石x3 + 木材/漂流木x2）", True))
        if not self.has_stone_axe:
            missing = []
            if self.stone < 1: missing.append(f"石头x{1-self.stone}")
            if self.wood < 1: missing.append(f"木材x{1-self.wood}")
            if missing: projects.append(("🪓 石斧", "❌ 缺少: " + ", ".join(missing), False))
            else: projects.append(("🪓 石斧", "▶️ [3] 建造（石头x1 + 木材x1）", True))
        if not self.has_stone_knife:
            missing = []
            if self.stone < 1: missing.append(f"石头x{1-self.stone}")
            if self.wood < 1: missing.append(f"木材x{1-self.wood}")
            if missing: projects.append(("🔪 石刀", "❌ 缺少: " + ", ".join(missing), False))
            else: projects.append(("🔪 石刀", "▶️ [4] 建造（石头x1 + 木材x1）", True))
        if not self.has_fishing_rod:
            missing = []
            if self.wood < 2: missing.append(f"木材x{2-self.wood}")
            if self.vine < 1: missing.append(f"藤蔓x{1-self.vine}")
            if missing: projects.append(("🎣 鱼竿", "❌ 缺少: " + ", ".join(missing), False))
            else: projects.append(("🎣 鱼竿", "▶️ [5] 建造（木材x2 + 藤蔓x1）", True))
        if not self.raft_built:
            if not self.has_stone_axe:
                projects.append(("⛵ 木筏", "❌ 需要先造石斧", False))
            else:
                missing = []
                if self.vine < 15: missing.append(f"藤蔓x{15-self.vine}")
                if self.wood + self.driftwood < 30: missing.append(f"木材/漂流木x{30-(self.wood+self.driftwood)}")
                if missing: projects.append(("⛵ 木筏", "❌ 缺少: " + ", ".join(missing), False))
                else: projects.append(("⛵ 木筏", f"▶️ [6] 建造（当前进度: {int(self.raft_progress/30*100)}%）", True))
        if self.raft_built and not self.raft_stored_safely:
            projects.append(("🏗️ 移动木筏", "▶️ [7] 拖到安全位置（避免风暴）", True))
        if not projects:
            print("  你还没有发现任何可以建造的东西。")
        else:
            for name, desc, available in projects:
                if available: print(f"  ✅ {desc}")
                else: print(f"  ❌ {desc}")
        print("\n  [0] 🔙 返回")
        choice = input("\n选择建造项目 (输入编号): ").strip()
        if choice == "0": return
        elif choice == "1" and not self.has_shelter: self.build_shelter()
        elif choice == "2" and not self.has_fire: self.build_fire()
        elif choice == "3" and not self.has_stone_axe: self.build_axe()
        elif choice == "4" and not self.has_stone_knife: self.build_knife()
        elif choice == "5" and not self.has_fishing_rod: self.build_rod()
        elif choice == "6" and not self.raft_built: self.build_raft()
        elif choice == "7" and self.raft_built and not self.raft_stored_safely: self.store_raft()
        else: print("❌ 无效选择")

    def build_shelter(self):
        if self.vine >= 2 and self.wood + self.driftwood >= 5:
            use_driftwood = min(self.driftwood, 5)
            self.driftwood -= use_driftwood
            need_wood = 5 - use_driftwood
            if need_wood > 0: self.wood -= need_wood
            self.vine -= 2
            self.has_shelter = True
            print("🏕️ 你建好了简陋的庇护所！可以遮风挡雨了。")
        else:
            print("❌ 材料不足：需要 藤蔓x2 + 木材/漂流木x5")

    def build_fire(self):
        if self.flint >= 3 and self.wood + self.driftwood >= 2:
            use_driftwood = min(self.driftwood, 2)
            self.driftwood -= use_driftwood
            need_wood = 2 - use_driftwood
            if need_wood > 0: self.wood -= need_wood
            self.flint -= 3
            self.has_fire = True
            print("🔥 你生起了火堆！夜间可以保暖，还能烹饪食物。")
        else:
            print("❌ 材料不足：需要 燧石x3 + 木材/漂流木x2")

    def build_axe(self):
        if self.stone >= 1 and (self.wood >= 1 or self.driftwood >= 1):
            self.stone -= 1
            if self.wood >= 1:
                self.wood -= 1
            else:
                self.driftwood -= 1
            self.has_stone_axe = True
            print("🪓 你制作了一把石斧！可以砍树和采集燧石了。")
        else:
            print("❌ 材料不足：需要 石头x1 + 木材/漂流木x1")

    def build_knife(self):
        if self.stone >= 1 and (self.wood >= 1 or self.driftwood >= 1):
            self.stone -= 1
            if self.wood >= 1:
                self.wood -= 1
            else:
                self.driftwood -= 1
            self.has_stone_knife = True
            self.has_weapon = True
            self.weapon_type = "石刀"
            print("🔪 你制作了一把石刀！可以战斗和采集藤蔓了。")
        else:
            print("❌ 材料不足：需要 石头x1 + 木材/漂流木x1")

    def build_rod(self):
        if self.wood >= 2 and self.vine >= 1:
            self.wood -= 2
            self.vine -= 1
            self.has_fishing_rod = True
            print("🎣 你制作了一根简易鱼竿！可以在沙滩钓鱼了。")
        else:
            print("❌ 材料不足：需要 木材x2 + 藤蔓x1")

    def build_raft(self):
        if self.raft_built:
            print("⛵ 木筏已经造好了！")
            return
        if not self.has_stone_axe:
            print("🪓 你需要石斧才能砍伐足够的木材来建造木筏。")
            return
        if self.wood + self.driftwood < 1 or self.vine < 1:
            print("❌ 材料不足，无法继续建造。")
            return
        if self.driftwood > 0: self.driftwood -= 1
        else: self.wood -= 1
        self.vine -= 1
        self.raft_progress += 1
        pct = int(self.raft_progress / 30 * 100)
        print(f"⛵ 木筏建造进度: {pct}%（{self.raft_progress}/30）")
        if self.raft_progress >= 30:
            self.raft_built = True
            self.raft_progress = 30
            print("🎉 木筏建造完成！你可以准备离开荒岛了！")
            print("   💡 还需要食物、淡水和航行方向。")

    def store_raft(self):
        if not self.raft_built:
            print("⛵ 你还没有建造木筏。")
            return
        if self.raft_stored_safely:
            print("🏗️ 木筏已经在安全位置了。")
            return
        self.raft_stored_safely = True
        print("🏗️ 你把木筏从沙滩拖到了内陆的树林中，藏在树丛后面。")
        print("   ✅ 现在暴风雨无法卷走它了！")

    def check_raft(self):
        if not self.raft_built:
            print("⛵ 你还没有建造木筏。")
            return
        status = "安全存放 ✅" if self.raft_stored_safely else "放在沙滩上 ⚠️"
        print(f"⛵ 木筏状态: {status}")
        if not self.raft_stored_safely:
            print("   ⚠️ 如果暴风雨来临时木筏还在沙滩上，有可能会被风浪卷走！")

    def explore(self):
        self.actions_today += 1
        if self.location == 0: self.explore_beach()
        elif self.location == 1: self.explore_middle()
        else: self.explore_center()

    def explore_beach(self):
        print("🏖️ 你在沙滩上漫步……")
        events = [
            ("捡到了一些漂流木", lambda: setattr(self, 'driftwood', self.driftwood + 1)),
            ("找到了几个贝壳", lambda: setattr(self, 'shells', self.shells + 1)),
            ("看到远处海面有船影……但太远了", lambda: None),
            ("什么也没发现", lambda: None),
        ]
        event, effect = random.choice(events)
        print(f"   {event}")
        if effect: effect()
        if not self.found_bottle and random.random() < 0.15:
            self.found_bottle = True
            print("\n🧴 你在沙滩上发现了一个漂流瓶！")
            print("   📜 字条上写着: '向西航行，你会找到迷雾港。'")
            self.has_direction = True

    def explore_middle(self):
        print("🌿 你在灌木丛中穿行……")
        events = [
            ("发现了一些野果", lambda: setattr(self, 'fruit', self.fruit + 3)),
            ("找到了一些藤蔓", lambda: setattr(self, 'vine', self.vine + 2)),
            ("发现了野兽的脚印", lambda: None),
            ("什么也没发现", lambda: None),
        ]
        event, effect = random.choice(events)
        print(f"   {event}")
        if effect: effect()

    def explore_center(self):
        print("🌳 你在中心树林中探索……")
        if not self.found_wreck and random.random() < 0.3:
            self.found_wreck = True
            print("\n🧭 你发现了一艘旧沉船的残骸！")
            print("   📖 船长的航海日志上写着：")
            print("   '迷雾港位于此岛正西方向，航行约需一天。'")
            self.has_direction = True
            return
        if not self.found_stone and random.random() < 0.2:
            self.found_stone = True
            print("\n🗿 你发现了一块神秘的石碑！")
            if self.has_direction:
                print("   💡 结合沉船地图，你确定迷雾港在西边。")
            else:
                print("   💡 你需要找到更多线索来确认方向。")
            return
        print("   💧 你听到了泉水的声音，附近还有可用的树木和石头。")

    def rest(self):
        if self.actions_today >= self.max_actions:
            print("⏰ 你已经很累了，今天就到这里吧。")
            return
        restore = 5 + random.randint(0, 3)
        self.hp = min(self.max_hp, self.hp + restore)
        self.actions_today += 1
        print(f"💤 你休息了一会儿，恢复了 {restore} HP（当前 HP: {self.hp}）")

    def eat(self):
        if self.fish_count > 0:
            self.fish_count -= 1
            self.food = min(10, self.food + 3)
            print(f"🐟 你生吃了一条鱼，饱食 +3（当前: {self.food}/10）")
            return
        if self.fruit > 0:
            self.fruit -= 1
            self.food = min(10, self.food + 2)
            self.water = min(10, self.water + 1)
            print(f"🍎 你吃了一些野果，饱食 +2 水分 +1（当前: {self.food}/10）")
            return
        print("🍽️ 你没有可食用的食物。")

    def drink(self):
        if self.water_units > 0:
            self.water_units -= 1
            self.water = min(10, self.water + 3)
            print(f"💧 你喝了淡水，水分 +3（当前: {self.water}/10）")
        else:
            print("💧 你没有储备淡水。")

    def use_herb(self):
        if self.herb > 0:
            self.herb -= 1
            restore = 5
            self.hp = min(self.max_hp, self.hp + restore)
            self.food = min(10, self.food + 1)
            print(f"🌿 你使用了药草，恢复 {restore} HP，饱食 +1")
        else:
            print("🌿 你没有药草。")

    def check_vitals(self):
        self.hp = max(0, min(self.max_hp, self.hp))
        self.water = max(0, min(10, self.water))
        self.food = max(0, min(10, self.food))
        if self.hp <= 0:
            self.alive = False
            print("\n💀 你倒下了……")

    def handle_storm(self):
        if self.day == 1 and self.storm_day is None:
            self.storm_day = random.choice([2, 3])
            print(f"\n💨 你感觉到海风中有一种不寻常的气息……（风暴将在第 {self.storm_day} 天夜里来临）")
        if self.storm_triggered or self.storm_day is None or self.day < self.storm_day:
            return
        if self.storm_day is not None and self.day == self.storm_day and not self.storm_triggered:
            self.storm_triggered = True
            self.storm_active = True
            self.storm_duration = 1 + random.randint(0, 1)
            print("\n" + "="*50)
            print("⛈️⛈️⛈️ 暴风雨来了！⛈️⛈️⛈️")
            print("="*50)
            print("狂风呼啸，暴雨倾盆而下！")
            if self.has_shelter:
                print("🏕️ 你在庇护所里，暂时安全。但外面风雨大作……")
                if self.raft_built and not self.raft_stored_safely:
                    if random.random() < 0.5:
                        print("💨 你听到沙滩方向传来巨响……")
                        print("   😱 你的木筏被风浪卷走了！！！")
                        self.raft_built = False
                        self.raft_progress = max(0, self.raft_progress - 15)
                        print("   💔 损失了一半材料，你需要重新收集。")
            else:
                print("💀 你没有任何遮蔽！暴雨中浑身湿透，失温严重！")
                self.hp -= 15
                if self.hp <= 0:
                    print("\n💀 你倒在了暴风雨中……")
                    self.alive = False
                    return
                print(f"❤️ 剩余 HP: {self.hp}")
            if self.raft_built and not self.raft_stored_safely and not self.has_shelter:
                if random.random() < 0.7:
                    print("💨 狂风卷走了你放在沙滩上的木筏！")
                    self.raft_built = False
                    self.raft_progress = max(0, self.raft_progress - 15)
        if self.storm_active and self.day > self.storm_day:
            self.storm_duration -= 1
            if self.storm_duration <= 0:
                self.storm_active = False
                print("\n☀️ 暴风雨终于停了……天空开始放晴。")

    def end_day(self):
        if self.period == 3 and not self.storm_active:
            if not self.has_shelter and not self.has_fire:
                self.hp -= 3
                print("🌙 夜晚寒冷，你没有庇护所和火堆，失温了。-3 HP")
            elif not self.has_shelter and self.has_fire:
                print("🌙 火堆让你暖和了一些，但没有庇护所，你睡不踏实。")
        self.day += 1
        self.period = 0
        self.actions_today = 0
        self.water -= 1
        self.food -= 1
        if self.water_units > 0 and self.water < 8:
            self.water_units -= 1
            self.water = min(10, self.water + 3)
        if self.water <= 0:
            self.hp -= 5
            print("💧 你严重缺水！-5 HP")
        if self.food <= 0:
            self.hp -= 5
            print("🍖 你饿得头晕眼花！-5 HP")
        self.hp = max(0, min(self.max_hp, self.hp))
        self.water = max(0, min(10, self.water))
        self.food = max(0, min(10, self.food))
        if self.hp <= 0:
            self.alive = False
            print("\n💀 你没能活过这一夜……")
            return
        self.handle_storm()
        print(f"\n🌅 第 {self.day} 天开始了。")

    def try_leave(self):
        if not self.raft_built:
            print("⛵ 你还没有建造木筏。")
            return
        issues = []
        if not self.has_direction:
            issues.append("你不知道该往哪个方向航行。")
        if self.food < 5:
            issues.append("你只有很少的食物（需要 5 份）。")
        if self.water_units < 5:
            issues.append("你只有很少的淡水（需要 5 份）。")
        if self.hp < 20:
            if self.hp >= 15 and self.herb > 0:
                print("💡 你虽然 HP 不足 20，但带了一份药草，可以支撑航行。")
            else:
                issues.append(f"你的身体状况不佳（HP {self.hp}，需要 ≥20 或 ≥15 且有药草）。")
        if issues:
            print("\n⛵ 你坐上木筏，但……")
            for issue in issues:
                print(f"   ❌ {issue}")
            print("\n💡 你再做点准备再试试吧。")
            return
        print("\n" + "="*50)
        print("🎉 你终于准备好离开了！")
        print("="*50)
        print(f"📅 你在荒岛上度过了 {self.day} 天。")
        print(f"🪵 木材: {self.wood} | 🪨 石头: {self.stone} | 🌿 藤蔓: {self.vine}")
        print(f"🐟 食物: {self.food} | 💧 淡水: {self.water_units}")
        print(f"🏕️ 庇护所: {'有' if self.has_shelter else '无'} | 🔥 火堆: {'有' if self.has_fire else '无'}")
        print("\n🌊 你推着木筏入海，向西航行……")
        print("   ...一天一夜后...")
        print("🏘️ 你看到了远处的炊烟和码头！")
        print("   ✅ 你成功到达了迷雾港！")
        print("="*50)
        self.escaped = True

    def run(self):
        print("\n" + "="*50)
        print("🏝️ 荒岛求生")
        print("="*50)
        print("""
你睁开眼。

咸涩的海风灌进鼻腔，耳边是潮水退去时沙砾摩擦的声响。
你躺在一片陌生的沙滩上，湿透的衣服紧贴皮肤，冰冷而沉重。
阳光刺得你眯起眼睛——天已经亮了。

你坐起身，头痛欲裂。你试图回忆自己是怎么来到这里的，
但脑子里只有一片空白。不记得名字，不记得家乡，不记得任何一张脸。

你低下头，看到自己身上只有：
一件破旧的衬衫、一条磨出线头的长裤、
一张被海水泡得发皱的纸片。

你把纸片摊开——上面画着一条歪歪扭扭的船，
和一串模糊的字迹。纸条早就被泡得不成样子，看不出什么东西。

你抬起头，环顾四周。

这是一个不大的岛屿，沙滩绕着海岸线延伸，
远处是一片低矮的绿色——灌木丛和树木。
再远一点，你看到岛的中心似乎有一片石林和更高的树木。

风吹过，带着陌生的植物气味。
你不知道这是什么地方，也不知道自己是谁。

但你知道一件事。

你不想死在这里。

你站了起来。沙子从你衣服上落下。
阳光正照在这座岛屿上，像一个安静而不怀好意的舞台。

你开始了自由行动......
""")
        input("按回车开始生存……")

        while self.alive and not self.escaped:
            self.show_status()
            self.show_actions()
            action = input("\n请输入行动: ").strip().lower()
            action_locked = self.actions_today >= self.max_actions
            locked_cmds = {"cw","cs","cv","cwater","cflint","pick","gather","fish","hunt","build","carrywater"}
            if action_locked and action in locked_cmds:
                print("⏰ 你今天已经精疲力竭，无法再采集或建造。可以吃东西、喝水、使用药草或等待明天。")
            elif action == "m1": self.move_to(0)
            elif action == "m2": self.move_to(1)
            elif action == "m3": self.move_to(2)
            elif action == "cw": self.collect_wood()
            elif action == "cs": self.collect_stone()
            elif action == "cv": self.collect_vine()
            elif action == "cwater": self.collect_water()
            elif action == "cflint": self.collect_flint()
            elif action == "pick": self.pick_beach()
            elif action == "gather": self.gather_middle()
            elif action == "fish": self.go_fish()
            elif action == "hunt": self.hunt()
            elif action == "eat": self.eat()
            elif action == "drink": self.drink()
            elif action == "build": self.build_menu()
            elif action == "carrywater": self.carry_water()
            elif action == "explore": self.explore()
            elif action == "rest": self.rest()
            elif action == "raft": self.check_raft()
            elif action == "store": self.store_raft()
            elif action == "useherb" or action == "herb": self.use_herb()
            elif action == "leave": self.try_leave()
            elif action == "night": self.end_day()
            elif action == "status": continue
            elif action == "help": self.show_actions()
            else: print("❌ 无效指令。输入 'help' 查看所有指令。")
            if self.hp <= 0:
                self.alive = False
                print("\n💀 你死了……")
                print(f"📅 你在荒岛上存活了 {self.day} 天。")
                break

        if self.escaped:
            print("\n🎉 恭喜你成功逃离荒岛！")
            print("   《迷雾港》的冒险即将开始...")
            print("   (小镇篇正在开发中)")
        if not self.alive:
            print("\n💀 游戏结束。")
            print(f"你没能离开荒岛，在第 {self.day} 天倒下了。")

if __name__ == "__main__":
    game = GameState()
    game.run()
