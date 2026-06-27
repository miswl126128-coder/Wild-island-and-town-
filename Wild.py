import random
import time
import os
import sys

# ==================== 游戏状态 ====================
class GameState:
    def __init__(self):
        # 基础状态
        self.hp = 30
        self.max_hp = 30
        self.day = 1
        self.alive = True
        self.escaped = False
        
        # 生存需求
        self.water = 10      # 满分10，每天消耗1
        self.food = 10       # 满分10，每天消耗1
        
        # 位置 (0=沙滩, 1=中部灌木, 2=中心区域)
        self.location = 0
        self.location_names = ["🏖️ 沙滩", "🌿 中部灌木丛", "🌳 中心石林"]
        
        # 时间 (每天4个时段)
        self.period = 0      # 0=清晨, 1=白天, 2=傍晚, 3=夜晚
        self.period_names = ["🌅 清晨", "☀️ 白天", "🌆 傍晚", "🌙 夜晚"]
        self.actions_today = 0
        self.max_actions_per_day = 6
        
        # 资源
        self.wood = 0
        self.stone = 0
        self.vine = 0
        self.fish = 0        # 食物来源
        self.fruit = 0       # 食物来源
        self.water_units = 5 # 淡水储备
        self.shells = 0
        self.hide = 0        # 兽皮
        self.bone = 0        # 骨头
        
        # 工具/建造
        self.has_stone_axe = False
        self.has_stone_knife = False
        self.has_fishing_rod = False
        self.has_shelter = False
        self.has_fire = False
        self.raft_progress = 0   # 0-20, 满20完成
        self.raft_built = False
        
        # 探索进度
        self.found_wreck = False   # 沉船日志（方向指引）
        self.found_bottle = False  # 漂流瓶
        self.explored_center = False
        
        # 天气
        self.weather = "晴朗"
        self.weather_timer = 0
        
        # 标记
        self.raft_stored_safely = False  # 木筏是否拖到安全位置
        
        # 战斗相关
        self.has_weapon = False
        self.weapon_type = "拳头"  # 拳头/石刀
        
        # 时间戳
        self.last_rain_check = 0
        
        # 日志（给玩家的提示线索）
        self.discovered_raft_need = False
        self.discovered_direction = False
        
    # ==================== 核心状态检查 ====================
    
    def check_survival_needs(self):
        """检查生存需求，返回是否需要消耗"""
        if self.water <= 0:
            self.hp -= 3
            return "💧 你严重缺水！"
        if self.food <= 0:
            self.hp -= 3
            return "🍖 你饿得头晕眼花！"
        return None
        
    def check_night_cold(self):
        """夜间检查是否失温"""
        if self.period == 3:  # 夜晚
            if self.weather in ["暴雨", "小雨"]:
                if not self.has_shelter:
                    self.hp -= 5
                    return "🌧️ 你没有任何遮蔽，暴雨中浑身湿透，失温严重！(-5 HP)"
                elif not self.has_fire:
                    self.hp -= 2
                    return "🌧️ 你有庇护所但太冷了，没有生火，冻得瑟瑟发抖。(-2 HP)"
            else:
                if not self.has_shelter and not self.has_fire:
                    self.hp -= 2
                    return "🌙 夜晚寒冷，你没有庇护所和火堆。(-2 HP)"
        return None
        
    def check_death(self):
        """检查是否死亡"""
        if self.hp <= 0:
            self.alive = False
            return True
        return False
        
    def end_day(self):
        """结束一天，推进时间"""
        self.day += 1
        self.period = 0
        self.actions_today = 0
        # 每天消耗
        self.water -= 1
        self.food -= 1
        # 淡水储备自动消耗
        if self.water_units > 0 and self.water < 8:
            self.water_units -= 1
            self.water = min(10, self.water + 3)
        # 天气变化
        self.update_weather()
        # 沙滩刷新
        if random.random() < 0.6:
            pass  # 在具体操作中体现
        
    def update_weather(self):
        """更新天气"""
        roll = random.random()
        if roll < 0.05:  # 5% 暴雨
            self.weather = "暴雨"
        elif roll < 0.15:  # 10% 小雨
            self.weather = "小雨"
        elif roll < 0.40:
            self.weather = "多云"
        else:
            self.weather = "晴朗"
            
    # ==================== 行动系统 ====================
    
    def take_action(self, action):
        """执行行动"""
        if not self.alive or self.escaped:
            return
            
        if self.actions_today >= self.max_actions_per_day:
            print("\n⏰ 你已经累了，今天不能再行动了。")
            print("   (选择 '结束今天' 来进入夜晚)")
            return
            
        # 天气影响
        weather_penalty = 0
        if self.weather == "暴雨":
            weather_penalty = 0.5
            print("⛈️ 暴雨倾盆，所有采集效率减半！")
        elif self.weather == "小雨":
            weather_penalty = 0.3
            print("🌧️ 下着小雨，采集效率略降。")
            
        # 执行具体行动
        if action == "explore":
            self.explore(weather_penalty)
        elif action == "collect_wood":
            self.collect_wood(weather_penalty)
        elif action == "collect_stone":
            self.collect_stone(weather_penalty)
        elif action == "collect_vine":
            self.collect_vine(weather_penalty)
        elif action == "collect_water":
            self.collect_water(weather_penalty)
        elif action == "hunt":
            self.hunt()
        elif action == "fish":
            self.fish()
        elif action == "build":
            self.build_menu()
        elif action == "rest":
            self.rest()
        elif action == "check_raft":
            self.check_raft()
        elif action == "move_to_beach":
            self.move_to(0)
        elif action == "move_to_middle":
            self.move_to(1)
        elif action == "move_to_center":
            self.move_to(2)
        elif action == "end_day":
            self.end_day_actions()
            return
        else:
            print("❓ 未知行动")
            
        # 消耗行动次数
        if action != "end_day" and action != "move_to_beach" and action != "move_to_middle" and action != "move_to_center":
            self.actions_today += 1
            
        # 检查生存需求
        need_msg = self.check_survival_needs()
        if need_msg:
            print(need_msg)
            
        # 检查夜间失温（如果是夜晚行动后）
        if self.period == 3:
            cold_msg = self.check_night_cold()
            if cold_msg:
                print(cold_msg)
                
        # 检查死亡
        if self.check_death():
            print("\n" + "="*50)
            print("💀 你死了...")
            print(f"📅 存活了 {self.day} 天")
            print("="*50)
            return
            
    def end_day_actions(self):
        """结束今天"""
        # 夜间失温检查
        cold_msg = self.check_night_cold()
        if cold_msg:
            print(cold_msg)
            
        if self.check_death():
            return
            
        print(f"\n🌙 第 {self.day} 天结束了。")
        self.end_day()
        print(f"🌅 第 {self.day} 天开始了！")
        
    # ==================== 移动系统 ====================
    
    def move_to(self, target):
        """移动到目标区域"""
        if target == self.location:
            print(f"你已经在 {self.location_names[target]} 了。")
            return
            
        # 移动到中心需要先探索中部
        if target == 2 and self.location == 0:
            print("🌿 你穿过中部灌木丛才能到达中心区域。")
            self.location = 1
            print(f"📍 你现在在 {self.location_names[1]}")
            return
            
        # 移动消耗半个行动
        self.actions_today += 0.5
        self.location = target
        print(f"📍 你来到了 {self.location_names[target]}")
        
        # 触发区域事件
        self.trigger_location_event()
        
    def trigger_location_event(self):
        """区域随机事件"""
        if self.location == 2 and not self.explored_center:
            self.explored_center = True
            print("\n🔍 你发现中心区域有一片石林和几棵大树，还有一处泉水！")
            print("   💡 这里可以采集木材、石头和淡水。")
            
        if self.location == 0 and random.random() < 0.2:
            print("\n📜 你注意到沙滩上有一个被冲上来的物品...")
            if random.random() < 0.5 and not self.found_bottle:
                self.found_bottle = True
                print("   🧴 是一个漂流瓶！里面有张字条：")
                print("   '向西航行...你会找到一个叫迷雾港的地方。'")
                self.discovered_direction = True
            else:
                print("   🪵 是一段漂流木！(+1 木材)")
                self.wood += 1
                
    # ==================== 采集系统 ====================
    
    def collect_wood(self, penalty=0):
        """采集木材"""
        if self.location < 2:
            print("🌳 这里没有大树，你需要到中心区域才能获得足够木材。")
            return
            
        base = 2 + random.randint(0, 2)
        if self.has_stone_axe:
            base += 2
        amount = max(1, int(base * (1 - penalty)))
        self.wood += amount
        print(f"🪵 你采集了 {amount} 份木材 (当前: {self.wood})")
        
        # 触发发现
        if not self.discovered_raft_need and self.wood >= 5:
            self.discovered_raft_need = True
            print("💡 你看着这些木头，心想：也许可以造点什么离开这里...")
            
    def collect_stone(self, penalty=0):
        """采集石头"""
        if self.location < 2:
            print("这里没有石头，你需要到中心区域。")
            return
            
        base = 1 + random.randint(0, 2)
        amount = max(1, int(base * (1 - penalty)))
        self.stone += amount
        print(f"🪨 你采集了 {amount} 块石头 (当前: {self.stone})")
        
    def collect_vine(self, penalty=0):
        """采集藤蔓"""
        if self.location == 0:
            print("沙滩上没有藤蔓，需要到中部或中心区域。")
            return
            
        base = 1 + random.randint(0, 2)
        if self.has_stone_knife:
            base += 1
        amount = max(1, int(base * (1 - penalty)))
        self.vine += amount
        print(f"🌿 你采集了 {amount} 根藤蔓 (当前: {self.vine})")
        
    def collect_water(self, penalty=0):
        """采集淡水"""
        if self.location != 2:
            print("只有中心区域的泉水可以采集淡水。")
            return
            
        amount = 2 + random.randint(0, 1)
        self.water_units += amount
        self.water = min(10, self.water + 2)
        print(f"💧 你采集了 {amount} 份淡水 (当前储备: {self.water_units}, 水分: {self.water}/10)")
        
    # ==================== 食物系统 ====================
    
    def fish(self):
        """钓鱼"""
        if not self.has_fishing_rod:
            print("🎣 你没有鱼竿，无法钓鱼。")
            print("   💡 用木材和藤蔓可以制作简易鱼竿。")
            return
            
        if self.location != 0:
            print("钓鱼需要在沙滩海边。")
            return
            
        if self.weather in ["暴雨", "小雨"]:
            success_rate = 0.6
        else:
            success_rate = 0.8
            
        if random.random() < success_rate:
            amount = 1 + random.randint(0, 1)
            self.fish += amount
            self.food = min(10, self.food + 1)
            print(f"🐟 你钓到了 {amount} 条鱼！ (当前食物: {self.food}/10)")
        else:
            print("🐟 今天鱼儿不太活跃，什么都没钓到。")
            
    def hunt(self):
        """狩猎（战斗）"""
        if self.location == 0:
            print("沙滩上没有野兽可狩猎。")
            return
            
        # 确定猎物
        prey = random.choice([
            ("野猪", 12, 3, 2),  # HP, 攻击, 防御
            ("巨鸟", 8, 2, 1),
            ("毒蛇", 6, 4, 0),
        ])
        name, hp, atk, defense = prey
        
        print(f"\n⚔️ 你遇到了 {name}！")
        print(f"   HP: {hp} | 攻击: {atk}")
        
        # 简易战斗
        player_atk = 3
        if self.has_stone_knife:
            player_atk = 6
        elif self.has_stone_axe:
            player_atk = 5
            
        while hp > 0 and self.hp > 0:
            # 玩家攻击
            damage = max(1, player_atk + random.randint(-1, 2) - defense)
            hp -= damage
            print(f"   💥 你造成 {damage} 点伤害！ ({name} HP: {hp})")
            
            if hp <= 0:
                print(f"   ✅ 击败了 {name}！")
                self.hide += 1
                self.bone += 1
                self.food = min(10, self.food + 2)
                print(f"   🥩 获得兽皮 x1, 骨头 x1, 食物 +2")
                return
                
            # 敌人反击
            enemy_damage = max(1, atk + random.randint(0, 2) - 1)
            self.hp -= enemy_damage
            print(f"   💢 {name} 反击，造成 {enemy_damage} 点伤害！ (你的HP: {self.hp})")
            
            if self.hp <= 0:
                print("💀 你被野兽击败了...")
                self.alive = False
                return
                
        print(f"✅ 战斗结束！当前 HP: {self.hp}")
        
    # ==================== 建造系统 ====================
    
    def build_menu(self):
        """建造菜单"""
        print("\n" + "="*40)
        print("🛠️ 建造菜单")
        print("="*40)
        print(f"当前材料: 木材{self.wood} | 石头{self.stone} | 藤蔓{self.vine}")
        
        options = []
        
        # 火堆
        if not self.has_fire:
            options.append(("1", "🔥 火堆 (木材x3 + 燧石x1)", self.build_fire))
        # 庇护所
        if not self.has_shelter:
            options.append(("2", "🏕️ 庇护所 (木材x5 + 藤蔓x3)", self.build_shelter))
        # 石斧
        if not self.has_stone_axe:
            options.append(("3", "🪓 石斧 (石头x2 + 木材x1)", self.build_axe))
        # 石刀
        if not self.has_stone_knife:
            options.append(("4", "🔪 石刀 (石头x1 + 木材x1)", self.build_knife))
        # 鱼竿
        if not self.has_fishing_rod:
            options.append(("5", "🎣 鱼竿 (木材x2 + 藤蔓x1)", self.build_rod))
        # 木筏
        if not self.raft_built:
            pct = int(self.raft_progress / 20 * 100)
            options.append(("6", f"⛵ 建造木筏 ({pct}% 进度) 木材x20 藤蔓x10", self.build_raft))
        # 移动木筏（安全存放）
        if self.raft_built and not self.raft_stored_safely:
            options.append(("7", "🏗️ 将木筏拖到内陆安全位置", self.store_raft))
            
        options.append(("0", "🔙 返回", None))
        
        for label, desc, _ in options:
            print(f"  [{label}] {desc}")
            
        choice = input("\n选择建造项目 (输入编号): ").strip()
        
        for label, desc, func in options:
            if choice == label and func:
                func()
                return
        if choice == "0":
            return
        print("❌ 无效选择")
        
    def build_fire(self):
        if self.wood >= 3 and self.stone >= 1:
            self.wood -= 3
            self.stone -= 1
            self.has_fire = True
            print("🔥 你生起了火堆！夜间可以保暖，还可以烹饪食物。")
        else:
            print("❌ 材料不足：需要 木材x3, 石头x1")
            
    def build_shelter(self):
        if self.wood >= 5 and self.vine >= 3:
            self.wood -= 5
            self.vine -= 3
            self.has_shelter = True
            print("🏕️ 你建好了简陋的庇护所！可以遮风挡雨了。")
        else:
            print("❌ 材料不足：需要 木材x5, 藤蔓x3")
            
    def build_axe(self):
        if self.stone >= 2 and self.wood >= 1:
            self.stone -= 2
            self.wood -= 1
            self.has_stone_axe = True
            print("🪓 你制作了一把石斧！砍树效率提升。")
        else:
            print("❌ 材料不足：需要 石头x2, 木材x1")
            
    def build_knife(self):
        if self.stone >= 1 and self.wood >= 1:
            self.stone -= 1
            self.wood -= 1
            self.has_stone_knife = True
            self.has_weapon = True
            self.weapon_type = "石刀"
            print("🔪 你制作了一把石刀！可以战斗和采集藤蔓了。")
        else:
            print("❌ 材料不足：需要 石头x1, 木材x1")
            
    def build_rod(self):
        if self.wood >= 2 and self.vine >= 1:
            self.wood -= 2
            self.vine -= 1
            self.has_fishing_rod = True
            print("🎣 你制作了一根简易鱼竿！可以在沙滩钓鱼了。")
        else:
            print("❌ 材料不足：需要 木材x2, 藤蔓x1")
            
    def build_raft(self):
        """建造木筏（分次进行）"""
        if self.raft_built:
            print("⛵ 木筏已经造好了！")
            return
            
        needed_wood = 20
        needed_vine = 10
        
        if self.raft_progress == 0:
            print("🪵 你需要收集 20 份木材和 10 根藤蔓来建造木筏。")
            
        if self.wood >= 2 and self.vine >= 1:
            # 每次建造消耗一定材料
            wood_used = min(3, self.wood, needed_wood - self.raft_progress // 2)
            vine_used = min(2, self.vine, (needed_vine - self.raft_progress // 2))
            # 简化：每投入2木材+1藤蔓 = 1进度
            while self.wood >= 2 and self.vine >= 1 and self.raft_progress < 20:
                self.wood -= 2
                self.vine -= 1
                self.raft_progress += 1
                
            pct = int(self.raft_progress / 20 * 100)
            print(f"⛵ 木筏建造进度: {pct}%")
            
            if self.raft_progress >= 20:
                self.raft_built = True
                self.raft_progress = 20
                print("🎉 木筏建造完成！你可以准备离开这个荒岛了！")
                print("   💡 不过你需要食物、淡水和航行方向。")
        else:
            print("❌ 材料不足：建造需要木材和藤蔓。")
            if self.wood < 2:
                print(f"   🪵 需要更多木材 (当前: {self.wood}/2)")
            if self.vine < 1:
                print(f"   🌿 需要更多藤蔓 (当前: {self.vine}/1)")
                
    def store_raft(self):
        """将木筏拖到安全位置"""
        if not self.raft_built:
            print("⛵ 你还没有建造木筏。")
            return
        if self.raft_stored_safely:
            print("🏗️ 木筏已经在安全位置了。")
            return
            
        self.raft_stored_safely = True
        print("🏗️ 你把木筏从沙滩拖到了内陆的树林中，藏在树丛后面。")
        print("   ✅ 现在暴风雨和风浪无法卷走它了！")
        
    def check_raft(self):
        """检查木筏状态"""
        if not self.raft_built:
            print("⛵ 你还没有建造木筏。")
            return
            
        status = "安全存放" if self.raft_stored_safely else "放在沙滩上 ⚠️"
        print(f"⛵ 木筏状态: {status}")
        if not self.raft_stored_safely:
            print("   ⚠️ 如果暴风雨来临时木筏还在沙滩上，有可能会被风浪卷走！")
            
    # ==================== 其他行动 ====================
    
    def rest(self):
        """休息恢复HP"""
        restore = 5 + random.randint(0, 3)
        self.hp = min(self.max_hp, self.hp + restore)
        print(f"💤 你休息了一会儿，恢复了 {restore} HP (当前HP: {self.hp})")
        
    def explore(self, penalty=0):
        """探索当前区域"""
        if self.location == 0:
            self.explore_beach()
        elif self.location == 1:
            self.explore_middle()
        else:
            self.explore_center()
            
    def explore_beach(self):
        """探索沙滩"""
        print("🏖️ 你在沙滩上漫步...")
        events = [
            ("捡到了一些漂流木", lambda: self.wood + 1),
            ("找到了一些贝壳", lambda: self.shells + 1),
            ("看到远处海面有船影...但太远了", lambda: None),
            ("什么也没发现", lambda: None),
        ]
        event, effect = random.choice(events)
        print(f"   {event}")
        if effect:
            effect()
            
        # 概率触发特殊事件
        if random.random() < 0.15 and not self.found_bottle:
            self.found_bottle = True
            print("   🧴 你在沙滩上发现了一个漂流瓶！")
            print("   📜 字条上写着: '向西航行，你会找到迷雾港。'")
            self.discovered_direction = True
            
    def explore_middle(self):
        """探索中部灌木丛"""
        print("🌿 你在灌木丛中穿行...")
        events = [
            ("发现了一些可食用的野果", lambda: self.fruit + 1),
            ("找到了一些藤蔓", lambda: self.vine + 1),
            ("遇到了野兽的脚印", lambda: None),
            ("发现了一处适合建庇护所的地方", lambda: None),
        ]
        event, effect = random.choice(events)
        print(f"   {event}")
        if effect:
            effect()
            
    def explore_center(self):
        """探索中心区域"""
        print("🌳 你在中心石林和树林中探索...")
        if not self.found_wreck:
            if random.random() < 0.4:
                self.found_wreck = True
                print("   🧭 你发现了一艘旧沉船的残骸！")
                print("   📖 船长的航海日志上写着：")
                print("   '迷雾港位于此岛正西方向，航行约需一天。'")
                self.discovered_direction = True
                return
        print("   💧 你看到了泉水和可用的树木。")

    # ==================== 离开系统 ====================
    
    def try_leave(self):
        """尝试离开荒岛"""
        if not self.raft_built:
            print("⛵ 你还没有建造木筏。")
            return
            
        # 检查条件（不提示玩家，通过尝试反馈）
        issues = []
        
        if not self.discovered_direction:
            issues.append("你不知道该往哪个方向航行。")
            
        if self.food < 3:
            issues.append("你只有很少的食物，不足以支撑航行。")
            
        if self.water_units < 3:
            issues.append("你只有很少的淡水，不足以支撑航行。")
            
        if self.hp < 15:
            issues.append("你的身体状况不佳，不适合出海。")
            
        if issues:
            print("⛵ 你坐上木筏，但...")
            for issue in issues:
                print(f"   ❌ {issue}")
            print("\n💡 你再做点准备再试试吧。")
            return
            
        # 成功离开！
        print("\n" + "="*50)
        print("🎉 你终于准备好离开了！")
        print("="*50)
        print(f"📅 你在荒岛上度过了 {self.day} 天。")
        print(f"🪵 木材: {self.wood} | 🪨 石头: {self.stone} | 🌿 藤蔓: {self.vine}")
        print(f"🐟 食物: {self.food} | 💧 淡水: {self.water_units}")
        print("\n🌊 你推着木筏入海，向西航行...")
        print("   ...一天一夜后...")
        print("🏘️ 你看到了远处的炊烟和码头！")
        print("   ✅ 你成功到达了迷雾港！")
        print("="*50)
        self.escaped = True
        
    # ==================== 主界面 ====================
    
    def show_status(self):
        """显示状态"""
        print("\n" + "="*50)
        print(f"🏝️ 荒岛生存 · 第 {self.day} 天 · {self.period_names[self.period]}")
        print("="*50)
        print(f"❤️ HP: {self.hp}/{self.max_hp}  |  💧 水分: {self.water}/10  |  🍖 食物: {self.food}/10")
        print(f"🌤️ 天气: {self.weather}  |  📍 {self.location_names[self.location]}")
        print(f"⏳ 今日行动: {self.actions_today}/{self.max_actions_per_day}")
        print("-"*50)
        print(f"🪵 木材:{self.wood}  🪨 石头:{self.stone}  🌿 藤蔓:{self.vine}")
        print(f"💧 淡水储备:{self.water_units}  🐟 鱼:{self.fish}  🍎 野果:{self.fruit}")
        print(f"🔥 火堆:{'✅' if self.has_fire else '❌'}  🏕️ 庇护所:{'✅' if self.has_shelter else '❌'}")
        print(f"🪓 石斧:{'✅' if self.has_stone_axe else '❌'}  🔪 石刀:{'✅' if self.has_stone_knife else '❌'}")
        print(f"🎣 鱼竿:{'✅' if self.has_fishing_rod else '❌'}  ⛵ 木筏:{'✅' if self.raft_built else f'{int(self.raft_progress/20*100)}%'}")
        print("="*50)
        
    def show_actions(self):
        """显示行动菜单"""
        print("\n📋 行动选择:")
        print("  [移动]")
        print(f"    m1 前往沙滩  m2 前往中部  m3 前往中心")
        print("  [采集]")
        print("    cw 采集木材  cs 采集石头  cv 采集藤蔓  cwtr 采集淡水")
        print("  [食物]")
        print("    fish 钓鱼  hunt 狩猎")
        print("  [建造]")
        print("    build 建造菜单")
        print("  [其他]")
        print("    explore 探索  rest 休息  raft 检查木筏")
        print("  [离开]")
        print("    leave 尝试离开荒岛")
        print("  [时间]")
        print("    night 结束今天")
        print("  [状态]")
        print("    status 查看状态")
        print("  [帮助]")
        print("    help 显示这条消息")

# ==================== 游戏主循环 ====================

def main():
    game = GameState()
    
    print("\n" + "="*50)
    print("🏝️ 荒岛求生")
    print("="*50)
    print("你在一个陌生的小岛上醒来...")
    print("你不记得自己是怎么来到这里的。")
    print("你只知道，你必须想办法活下去，并离开这里。")
    print("="*50)
    
    while game.alive and not game.escaped:
        game.show_status()
        game.show_actions()
        
        action = input("\n请输入行动: ").strip().lower()
        
        # 移动
        if action == "m1":
            game.move_to(0)
        elif action == "m2":
            game.move_to(1)
        elif action == "m3":
            game.move_to(2)
        # 采集
        elif action == "cw":
            game.collect_wood()
        elif action == "cs":
            game.collect_stone()
        elif action == "cv":
            game.collect_vine()
        elif action == "cwtr":
            game.collect_water()
        # 食物
        elif action == "fish":
            game.fish()
        elif action == "hunt":
            game.hunt()
        # 建造
        elif action == "build":
            game.build_menu()
        # 其他
        elif action == "explore":
            game.explore()
        elif action == "rest":
            game.rest()
        elif action == "raft":
            game.check_raft()
        # 离开
        elif action == "leave":
            game.try_leave()
        # 时间
        elif action == "night":
            game.end_day_actions()
        # 状态
        elif action == "status":
            continue
        # 帮助
        elif action == "help":
            game.show_actions()
        else:
            print("❌ 无效指令。输入 'help' 查看所有指令。")
            
        # 检查死亡
        if game.check_death():
            break
            
    if game.escaped:
        print("\n🎉 恭喜你成功逃离荒岛！")
        print("   《迷雾港》的冒险即将开始...")
        print("   (小镇篇正在开发中)")
        
    if game.alive == False:
        print("\n💀 游戏结束。")
        print(f"你没能离开荒岛，在第 {game.day} 天倒下了。")

if __name__ == "__main__":
    main()
