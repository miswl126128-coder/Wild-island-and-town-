import random
import time
import os

class GameState:
    def __init__(self):
        self.hp = 26
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
        self.driftwood = 3
        self.stone = 2   # ★ 改动1：开局赠送一根漂流木
        self.stone = 0
        self.vine = 0
        self.flint = 0
        self.fish_count = 0
        self.grouper_count = 0
        self.shell_count = 0  # 可用作鱼饵的贝壳数量
        self.shell_inventory = {}  # 各类贝壳数量
        self.special_shells = {}  # 特殊贝壳（暴雨后）
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
        self.has_compass = False
        self.found_treasure = False
        self.unlocked_direct_m3 = False
        self.meat = 0
        self.first_visit_m2 = True
        self.first_visit_m3 = True
        self.first_pick = True
        self.first_fruit = True
        self.first_shell = True
        self.has_drunk_water = False
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
        raft_pct = int((self.raft_progress / 25) * 100) if self.raft_progress > 0 else 0
        raft_status = f"{raft_pct}%" if not self.raft_built else "✅ 已造好"
        print(f"🏕️ 庇护所:{shelter_status}  🔥 火堆:{fire_status}  🪓 石斧:{axe_status}")
        print(f"🎣 鱼竿:{rod_status}  ⛵ 木筏:{raft_status}")
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
        print("    cook  用椰子壳烹饪贝类（凤凰螺/夜光螺，需火堆+椰子壳）")
        print("    eatshell  生吃凤尾扇贝（饱食=10）")
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
            if self.unlocked_direct_m3:
                # 已解锁直达
                self.location = 2
                self.actions_today += 0.5
                print(f"📍 你直接前往 {self.location_names[2]}。")
            else:
                # 第一次必须经过灌木丛
                print("🌿 你穿过中部灌木丛，向中心树林前进……")
                self.location = 1
                print(f"📍 你现在在 {self.location_names[1]}，再输入 m3 可继续前往中心树林。")
                self.actions_today += 0.5
            return
        self.location = target
        if target == 1 and self.first_visit_m2:
            self.first_visit_m2 = False
            print(f"📍 你来到了 {self.location_names[target]}")
            print("   🌿 灌木丛里长满了植物，你随手摘了些。")
            self.fruit += 3
            self.vine += 1
            print(f"   🍎 获得野果 x3（当前: {self.fruit}）")
            print(f"   🌿 获得藤蔓 x1（当前: {self.vine}）")
            print("   💡 野果可以直接食用（eat），藤蔓可以用于建造——输入 build 查看！")
            print("   ⚠️ 有些蘑菇看起来很奇怪，采集时要小心分辨。")
            return
        if target == 2 and not self.unlocked_direct_m3:
            self.unlocked_direct_m3 = True
            print(f"📍 你来到了 {self.location_names[target]}")
            print("   💡 你已熟悉前往中心树林的路线，下次可以从沙滩直接过来。")
            return
        if target == 2 and self.first_visit_m3:
            self.first_visit_m3 = False
            print(f"📍 你来到了 {self.location_names[target]}")
            print("   🌳 这里可以采石头（cs）、砍树（cw）、采燧石（cflint，需石斧）。")
            print("   💧 你听到泉水声！输入 cwater 可以补满水分。")
            print("   ⚠️ 砍树会消耗 HP、饱食和水分，注意自身状态！")
            return
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
        if random.random() < 0.3:
            self.coconut += 1
            print(f"🥥 你发现了一个椰子壳！（当前: {self.coconut}）")
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
        self.has_drunk_water = True
        print(f"💧 你从泉水处采集了 {amount} 份淡水（储备: {self.water_units}，当前水分: {self.water}/10）")

    def cook_shells(self):
        """用椰子壳煮贝壳"""
        cookable = {k: v for k, v in self.shell_inventory.items() 
                   if k in ["中等凤凰螺", "夜光螺"] and v > 0}
        if not cookable:
            print("🥥 没有可以烹饪的贝类（凤凰螺或夜光螺）。")
            return
        if self.coconut < 1:
            print("🥥 你需要椰子壳才能烹饪。")
            return
        if not self.has_fire:
            print("🔥 你需要先生火。")
            return
        print("\n可烹饪的贝类：")
        items = list(cookable.items())
        for i, (name, count) in enumerate(items):
            print(f"  [{i+1}] {name} × {count}")
        print("  [0] 返回")
        choice = input("\n选择烹饪（输入编号）: ").strip()
        if choice == "0":
            return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                name, count = items[idx]
                self.shell_inventory[name] -= 1
                self.coconut -= 1
                self.food = min(10, self.food + 10)
                self.actions_today += 1
                print(f"🍲 你用椰子壳煮熟了{name}，饱食=10！（当前: {self.food}/10）")
        except:
            print("❌ 无效选择")

    def eat_special_shell(self):
        """吃凤尾扇贝（生吃）"""
        count = self.shell_inventory.get("凤尾扇贝", 0)
        if count <= 0:
            print("🐚 你没有凤尾扇贝。")
            return
        self.shell_inventory["凤尾扇贝"] -= 1
        self.food = 10
        print(f"🐚 你生吃了一个凤尾扇贝，饱食=10！（当前: {self.food}/10）")

    def dig_stone(self):
        """挖掘石碑下的宝藏"""
        if self.location != 2:
            print("❌ 这里没有什么可以挖的。")
            return
        if not self.found_stone:
            print("❌ 你还没有发现石碑。")
            return
        if self.found_treasure:
            print("📦 石碑下已经空了，宝藏你已经带走了。")
            return
        self.found_treasure = True
        self.actions_today += 1
        print("\n⛏️ 你在石碑底部挖掘……")
        print("   泥土松动了，你挖出一个羊皮包裹的防水信封。")
        print("   你小心展开——")
        print("\n   📜 这是一份信托基金证明。")
        print("   持有人：不记名")
        print("   签发人：E. Musk")
        print("   兑换机构：迷雾港信托行")
        print("   内容：黄金礁岛遗产基金壹份，凭此证明可于迷雾港信托行领取。")
        print("\n   你将信封小心收好。也许，这就是去迷雾港的另一个理由。")

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
            if self.first_pick:
                self.first_pick = False
                print("   💡 每天来沙滩看看，潮水会带来新的漂流木，说不定有意外收获！")
        else:
            shell_types = ["蛤蜊壳", "小扇贝", "青口壳"]
            shell_name = random.choice(shell_types)
            amount = random.randint(1, 5)
            self.shells += amount
            self.shell_count += amount  # 可用作鱼饵
            if shell_name not in self.shell_inventory:
                self.shell_inventory[shell_name] = 0
            self.shell_inventory[shell_name] += amount
            print(f"🐚 你捡到了 {amount} 个{shell_name}（当前贝壳总计: {self.shells}）")
            if self.first_shell:
                self.first_shell = False
                print("   💡 贝壳可以当鱼饵使用，钓鱼成功率从70%提升到90%！")
        # 特殊贝壳拾取
        if self.special_shells:
            for name, count in list(self.special_shells.items()):
                if count > 0:
                    print(f"✨ 你发现了 {count} 个{name}！")
                    if name == "凤尾扇贝":
                        print(f"   💡 凤尾扇贝可生吃，饱食=10。")
                        self.special_shells[name] = 0
                        if "凤尾扇贝" not in self.shell_inventory:
                            self.shell_inventory["凤尾扇贝"] = 0
                        self.shell_inventory["凤尾扇贝"] += count
                    else:
                        print(f"   ⚠️ {name}不可生吃，需用椰子壳煮熟后食用，饱食=10。")
                        self.special_shells[name] = 0
                        if name not in self.shell_inventory:
                            self.shell_inventory[name] = 0
                        self.shell_inventory[name] += count
            self.special_shells = {}
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
        # 必得野果
        fruit_amount = random.randint(2, 3)
        self.fruit += fruit_amount
        self.water = min(10, self.water + 1)
        print(f"🍎 你发现了 {fruit_amount} 个野果！（当前: {self.fruit}）")
        if self.first_fruit:
            self.first_fruit = False
            print("   💡 野果可以直接食用，输入 eat 补充饱食和水分。")
        # 额外随机收获
        if random.random() < 0.3:
            self.herb += 1
            print(f"🌿 你找到了一株药草！（当前: {self.herb}）")
            print("   💡 药草可以治疗 +5HP，输入 herb 使用。")
        if random.random() < 0.2:
            amount = random.randint(1, 2)
            self.vine += amount
            print(f"🌿 你割下了 {amount} 根藤蔓！（当前: {self.vine}）")
        if random.random() < 0.05:
            self.hp -= 5
            print("🍄 你误食了毒蘑菇！-5 HP")
        self.check_vitals()

    def show_hint(self):
        """显示当前建议"""
        hints = []
        if not self.has_shelter:
            hints.append("⚠️ 你还没有庇护所！风暴来临时没有庇护所会损失大量HP，优先建造庇护所。")
        if not self.has_fire:
            hints.append("💡 建议尽快生火，夜晚没有火堆会失温扣血。")
        if not self.has_stone_axe:
            hints.append("💡 先采石头+漂流木造石斧，石斧是砍树和采燧石的前提。")
        if self.hp <= 5:
            hints.append("🚨 HP极低！立刻rest休息或使用药草恢复血量！")
        if self.food <= 3:
            hints.append("🚨 饱食不足！去灌木丛gather野果，或去沙滩钓鱼补充食物。")
        if self.water <= 3:
            hints.append("🚨 水分不足！去中心泉水cwater补充淡水。")
        if self.actions_today >= self.max_actions - 2:
            hints.append("⏰ 行动力快耗尽了，记得eat和drink再结束今天。")
        if self.location in [1, 2] and self.food <= 5:
            hints.append("🐗 这里似乎有野兽出没，也许可以尝试狩猎（hunt）获取食物。")
        if not hints:
            hints.append("✅ 状态不错！优先顺序：庇护所→火堆→食物储备→木筏。")
        print("\n📖 当前建议：")
        for h in hints:
            print(f"  {h}")

    def go_fish(self):
        if self.location != 0:
            print("🎣 钓鱼需要在沙滩海边。")
            return
        if not self.has_fishing_rod:
            print("🎣 你还没有鱼竿。需要木材和藤蔓制作。")
            return
        self.actions_today += 1
        # 贝壳鱼饵
        use_bait = False
        if self.shell_count > 0:
            success_rate = 0.9
            grouper_rate = 0.7
            use_bait = True
            self.shell_count -= 1
            print("🐚 你用贝壳作为鱼饵。")
        else:
            success_rate = 0.7
            grouper_rate = 0.5
        # 傍晚/夜晚才有青石斑鱼
        is_evening = self.period in [2, 3]
        common_fish = ["雀鲷", "小鲻鱼", "迷你沙丁鱼", "小银鱼", "小青花鱼"]
        if random.random() < success_rate:
            caught_name = random.choice(common_fish)
            self.fish_count += 1
            food_val = 3
            print(f"🐟 你钓到了一条{caught_name}！生吃饱食+3（当前鱼: {self.fish_count}）")
            # 傍晚额外青石斑鱼概率
            if is_evening and random.random() < grouper_rate:
                self.grouper_count = getattr(self, 'grouper_count', 0) + 1
                print(f"🐠 额外钓到一条青石斑鱼！生吃饱食+6，火烤饱食=10（当前: {self.grouper_count}）")
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
        if self.has_stone_axe:
            player_atk = 6
            print("   🪓 你挥舞石斧，气势逼人！")
        while hp > 0 and self.hp > 0:
            damage = max(1, player_atk + random.randint(-1, 2) - defense)
            hp -= damage
            print(f"   💥 你造成 {damage} 点伤害！（{name} HP: {hp}）")
            if hp <= 0:
                print(f"   ✅ 击败了 {name}！")
                self.hide += 1
                self.bone += 2
                self.meat = getattr(self, "meat", 0) + 3
                self.food = 10
                print(f"   🥩 获得兽皮 x1, 兽骨 x2, 兽肉 x3，饱食=10！")
                print(f"   （兽皮: {self.hide} | 兽骨: {self.bone} | 兽肉: {self.meat}）")
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
        # 固定编号显示，编号永远对应同一项目
        def show_item(num, name, built, can_build, desc, missing_list):
            if built:
                print(f"  ✅ [{num}] {name}（已完成）")
            elif can_build:
                print(f"  ✅ [{num}] {name} - {desc}")
            else:
                print(f"  ❌ [{num}] {name} - 缺少: " + ", ".join(missing_list))

        # 1 庇护所
        missing = []
        if self.vine < 2: missing.append(f"藤蔓x{2-self.vine}")
        if self.wood + self.driftwood < 5: missing.append(f"木材/漂流木x{5-(self.wood+self.driftwood)}")
        show_item(1, "🏕️ 庇护所", self.has_shelter, not missing, "建造（藤蔓x2 + 木材/漂流木x5）", missing)

        # 2 火堆
        missing = []
        if self.flint < 3: missing.append(f"燧石x{3-self.flint}")
        if self.wood + self.driftwood < 2: missing.append(f"木材/漂流木x{2-(self.wood+self.driftwood)}")
        show_item(2, "🔥 火堆", self.has_fire, not missing, "建造（燧石x3 + 木材/漂流木x2）", missing)

        # 3 石斧
        missing = []
        if self.stone < 1: missing.append(f"石头x{1-self.stone}")
        if self.wood + self.driftwood < 1: missing.append(f"木材/漂流木x{1-(self.wood+self.driftwood)}")
        show_item(3, "🪓 石斧", self.has_stone_axe, not missing, "建造（石头x1 + 木材/漂流木x1）", missing)

        # 石刀已移除

        # 5 鱼竿
        missing = []
        if self.wood < 1: missing.append(f"木材x{1-self.wood}")
        if self.vine < 1: missing.append(f"藤蔓x{1-self.vine}")
        show_item(5, "🎣 鱼竿", self.has_fishing_rod, not missing, "建造（木材x1 + 藤蔓x1）", missing)

        # 6 木筏
        if not self.has_stone_axe:
            print(f"  ❌ [6] ⛵ 木筏 - 需要先造石斧")
        elif self.raft_built:
            print(f"  ✅ [6] ⛵ 木筏（已完成）")
        else:
            missing = []
            if self.vine < 10: missing.append(f"藤蔓x{10-self.vine}")
            if self.wood + self.driftwood < 25: missing.append(f"木材/漂流木x{25-(self.wood+self.driftwood)}")
            if missing:
                print(f"  ❌ [6] ⛵ 木筏（进度{int(self.raft_progress/30*100)}%）- 缺少: " + ", ".join(missing))
            else:
                print(f"  ✅ [6] ⛵ 木筏 - 建造（当前进度: {int(self.raft_progress/30*100)}%）")

        # 7 移动木筏
        if self.raft_built and not self.raft_stored_safely:
            print(f"  ✅ [7] 🏗️ 移动木筏 - 拖到安全位置（避免风暴）")
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
            print(f"📦 剩余材料：木材{self.wood} | 漂流木{self.driftwood} | 藤蔓{self.vine}")
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
            print(f"📦 剩余材料：木材{self.wood} | 漂流木{self.driftwood} | 燧石{self.flint}")
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
            print(f"📦 剩余材料：石头{self.stone} | 木材{self.wood} | 漂流木{self.driftwood}")
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
        if self.wood >= 1 and self.vine >= 1:
            self.wood -= 1
            self.vine -= 1
            self.has_fishing_rod = True
            print("🎣 你制作了一根简易鱼竿！可以在沙滩钓鱼了。")
            print(f"📦 剩余材料：木材{self.wood} | 藤蔓{self.vine}")
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
        pct = int(self.raft_progress / 25 * 100)
        print(f"⛵ 木筏建造进度: {pct}%（{self.raft_progress}/25）")
        print(f"📦 剩余材料：木材{self.wood} | 漂流木{self.driftwood} | 藤蔓{self.vine}")
        if pct >= 60 and pct < 65:
            print("💡 看来自己很快就要离开这座岛了！也许需要准备好充足的食物和水源，确保自己能够活着到达迷雾港。")
        if pct >= 90 and pct < 96:
            print("💡 木筏快造好了！看着自己的储备物资，要不要带走些东西？")
        if self.raft_progress >= 25:
            self.raft_built = True
            self.raft_progress = 25
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
        # 第8天强制触发未发现的内容
        force = self.day >= 8
        if not self.found_wreck and (force or random.random() < 0.4):
            self.found_wreck = True
            print("\n🧭 你发现了一艘旧沉船的残骸！")
            print("   船体已腐朽大半，但船舱里有一本保存尚好的航海日记。")
            print("\n   📖 你翻开日记……")
            print("   他们是为了荒岛的宝藏而来。")
            print("   一路艰辛，终于到达了这座岛——")
            print("   这座荒岛曾是富商 E. Musk 的私人财产，名为黄金礁岛。")
            print("   他放出豪言：「得此海藏者，富甲四海。」")
            print("\n   日记记录了船员们登岛后的艰难求生，伤亡接连发生……")
            print("   最后一篇日记写于某个雨夜，此后再无记录。")
            print("\n   📜 日记夹层里，你发现了一张泛黄的航海地图和一枚指南针。")
            print("   你晃了晃指南针，对着太阳的方向转了转——索性它还能用。")
            print("   地图上标注着：迷雾港，正西方向，约一天航程。")
            self.has_direction = True
            self.has_compass = True
            return
        if not self.found_stone and (force or random.random() < 0.4):
            self.found_stone = True
            print("\n🗿 你在树林深处发现了一块石碑。")
            print("   石碑古旧，青苔遍布，静静矗立在此不知多少年了。")
            print("   上面刻着两行字：")
            print("\n   Dig not the sand, sail not afar,")
            print("   All gifts abide beneath my guard.")
            print("\n   不必掘沙，不必奔赴沧海，")
            print("   全部馈赠，皆由我在此镇守。")
            return
        print("   💧 你听到了泉水的声音，附近还有可用的树木和石头。")

    def rest(self):
        if self.actions_today >= self.max_actions:
            print("⏰ 你已经很累了，今天就到这里吧。")
            return
        restore = 8 + random.randint(0, 3)
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
            self.storm_day = 3
            print(f"\n💨 你感觉到海风中有一种不寻常的气息……（风暴将在第3天夜里来临）")
        # 第4天之后10%概率随机暴风雨
        if self.storm_triggered and self.day > 3 and not self.storm_active:
            if random.random() < 0.10:
                self.storm_active = True
                self.storm_duration = 1
                print("\n" + "="*50)
                print("⛈️⛈️⛈️ 突然间暴风雨又来了！⛈️⛈️⛈️")
                print("="*50)
                print("狂风呼啸，暴雨倾盆而下！")
                if self.has_shelter:
                    print("🏕️ 你在庇护所里，暂时安全。")
                else:
                    self.hp -= 10
                    self.hp = max(0, self.hp)
                    print(f"💀 你没有庇护所！暴雨中浑身湿透，失温严重！")
                    print(f"❤️ 剩余 HP: {self.hp}")
            return
        if self.storm_triggered or self.storm_day is None or self.day < self.storm_day:
            return
        if self.storm_day is not None and self.day == self.storm_day and not self.storm_triggered:
            self.storm_triggered = True
            self.storm_active = True
            self.storm_duration = 1
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
                # 暴雨次日沙滩出现特殊贝壳
                self.special_shells = {
                    "凤尾扇贝": 4,
                    "中等凤凰螺": 4,
                    "夜光螺": 4
                }
                print("🐚 风暴过后，沙滩上出现了一些不寻常的贝类！去沙滩看看吧。")

    def end_day(self):
        if self.period == 3 and not self.storm_active:
            if not self.has_shelter and not self.has_fire:
                self.hp -= 3
                print("🌙 夜晚寒冷，你没有庇护所和火堆，失温了。-3 HP")
            elif not self.has_shelter and self.has_fire:
                print("🌙 火堆让你暖和了一些，但没有庇护所，你睡不踏实。")
        self.handle_storm()
        self.day += 1
        self.period = 0
        self.actions_today = 0
        self.water -= 1
        self.food -= 1
        if self.water_units > 0 and self.water < 8:
            self.water_units -= 1
            self.water = min(10, self.water + 3)
        if self.water <= 0:
            self.hp -= 3
            print("💧 你严重缺水！-3 HP")
        if self.food <= 0:
            self.hp -= 3
            print("🍖 你饿得头晕眼花！-3 HP")
        self.hp = max(0, min(self.max_hp, self.hp))
        self.water = max(0, min(10, self.water))
        self.food = max(0, min(10, self.food))
        if self.hp <= 0:
            self.alive = False
            print("\n💀 你没能活过这一夜……")
            return
        print(f"\n🌅 第 {self.day} 天开始了。")

    def pack_cargo(self):
        """装载携带物资"""
        print("\n" + "="*50)
        print("🎒 木筏空间有限，选择要带走的物资")
        print("="*50)
        print("（这些物资到迷雾港可以兑换金币）")

        cargo = {}
        limits = {
            "燧石": (self.flint, 50),
            "药草": (self.herb, 20),
            "石斧": (1 if self.has_stone_axe else 0, 3),
        }
        # 贝壳类
        for name in ["蛤蜊壳","小扇贝","青口壳","凤尾扇贝","中等凤凰螺","夜光螺"]:
            amt = self.shell_inventory.get(name, 0)
            if amt > 0:
                limits[name] = (amt, 15)
        # 鱼类
        fish_names = ["雀鲷","小鲻鱼","迷你沙丁鱼","小银鱼","小青花鱼"]
        total_fish = self.fish_count
        if total_fish > 0:
            limits["普通鱼"] = (total_fish, 5)
        if self.grouper_count > 0:
            limits["青石斑鱼"] = (self.grouper_count, 5)
        if self.hide > 0:
            limits["兽皮"] = (self.hide, 5)
        if self.bone > 0:
            limits["兽骨"] = (self.bone, 5)
        if self.meat > 0:
            limits["兽肉"] = (self.meat, 5)

        if not limits:
            print("你没有可带走的物资。")
            return cargo

        items = [(k, v) for k, v in limits.items() if v[0] > 0]
        if not items:
            print("你没有可带走的物资。")
            return cargo

        print("\n可携带物资（格式：数量/上限）：")
        for i, (name, (have, cap)) in enumerate(items):
            print(f"  [{i+1}] {name}  你有:{have}  上限:{cap}")
        print("  [0] 完成装载出发")

        while True:
            choice = input("\n选择物资编号（输入编号和数量，如 1 10）: ").strip()
            if choice == "0":
                break
            try:
                parts = choice.split()
                idx = int(parts[0]) - 1
                amt = int(parts[1]) if len(parts) > 1 else 1
                if 0 <= idx < len(items):
                    name, (have, cap) = items[idx]
                    amt = min(amt, have, cap)
                    cargo[name] = cargo.get(name, 0) + amt
                    print(f"✅ 已装载 {amt} 个{name}（本次合计: {cargo[name]}）")
                else:
                    print("❌ 无效编号")
            except:
                print("❌ 格式错误，请输入如：1 10")
        return cargo

    def try_leave(self):
        if not self.raft_built:
            print("⛵ 木筏还没造完，无法出发。")
            return
        issues = []
        if not self.has_direction:
            issues.append("你还没有找到航行方向（需要发现沉船获取地图和指南针）。")
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

        # 装载物资
        cargo = self.pack_cargo()

        print("\n" + "="*50)
        print("🎉 你终于准备好离开了！")
        print("="*50)
        print(f"📅 你在荒岛上度过了 {self.day} 天。")
        print(f"❤️ HP: {self.hp} | 🐟 食物: {self.food} | 💧 淡水: {self.water_units}")
        if cargo:
            print("\n🎒 携带物资：")
            for name, amt in cargo.items():
                print(f"   {name} × {amt}")
        print("\n🌊 你推着木筏入海，向西航行……")
        print("   ...一天一夜后...")
        print("🏘️ 你看到了远处的炊烟和码头！")
        print("   ✅ 你成功到达了迷雾港！")
        if cargo:
            print("\n💰 你带来的物资在小镇可以兑换金币，好好利用吧！")
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

你看了看身边的漂流木，可以利用起来。
看了看远处有些昏暗的云，海风中似乎有风暴的气息……
趁着天色还早，你决定先了解这片岛的情况，看看有没有需要的东西，确保自己能够活下去。

你环顾四周，试着记住这座岛的样子。
身边躺着三根漂流木，还有两块石头，有些干涸的血迹——似乎是被冲上岸时脑袋磕伤留下的。
灌木丛里隐约有些红色的果实，但也有些不认识的蘑菇，得小心分辨。
再往里走，树林深处传来若有若无的泉水声。

你开始了自由行动......
""")
        print("\n💡 你看了看手边的漂流木和石头——也许可以做点什么。输入 build 查看建造菜单。")
        input("按回车开始生存……")

        while self.alive and not self.escaped:
            self.show_status()
            self.show_actions()
            action = input("\n请输入行动: ").strip().lower()
            action_locked = self.actions_today >= self.max_actions
            locked_cmds = {"cw","cs","cv","cwater","cflint","pick","gather","fish","hunt","carrywater","cook"}
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
            elif action == "cook": self.cook_shells()
            elif action == "eatshell": self.eat_special_shell()
            elif action == "explore": self.explore()
            elif action == "rest": self.rest()
            elif action == "raft": self.check_raft()
            elif action == "store": self.store_raft()
            elif action == "useherb" or action == "herb": self.use_herb()
            elif action == "hint": self.show_hint()
            elif action == "dig": self.dig_stone()
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
