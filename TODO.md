# TODO - Roguelike Dungeon Explorer

## 🎨 Pixel Art & Visual Improvements

### High Priority

- [ ] **Fix Treasure Crown Icon Bottom Corners**
  - Current: Bottom corners are transparent `[0, 2, 2, 2, 2, 2, 0]`
  - Issue: May look incomplete or odd
  - Consider: Revert to solid bottom `[2, 2, 2, 2, 2, 2, 2]` or try different shapes
  - File: `PixelArtAssets.py` - Line 44 (TREASURE icon)
  - Test with: `python PixelArtAssets.py` or `preview_pixel_art.bat`

- [ ] **Review All Room Icon Designs**
  - Boss (Red Skull): ✓ Looks good
  - Treasure (Yellow Crown): ⚠️ Check bottom corners
  - Shop (Money Bag): ✓ Looks good
  - Secret (Purple ?): ✓ Looks good
  - Super Secret (Cyan Sparkle): ✓ Looks good

### Medium Priority

- [ ] **Add More Pixel Art Icons**
  - Item icons for minimap (show collected items)
  - Weapon power-up icons
  - Special effect indicators
  - Status effect icons

- [ ] **Create Animated Icons**
  - Blinking/pulsing treasure room icon
  - Animated boss room icon (breathing skull?)
  - Sparkle animation for super secret rooms
  - Add frame-based animation system to `PixelArtRenderer`

### Low Priority

- [ ] **Icon Size Variations**
  - Create larger versions for room entrance screens
  - Create smaller versions for inventory UI
  - Add scaling parameter to renderer

---

## 🐛 Bug Fixes

### Fixed ✓

- [x] **MazeGame.py Line 802 Error**
  - Error: `Cannot access attribute "boss_rooms"`
  - File: `MazeGame.py` - Line 802
  - Issue: `self.boss_rooms` doesn't exist
  - Fix: Removed reference to non-existent boss_rooms (boss room is in self.rooms)

- [x] **MazeGame.py Line 2228 Error**
  - Error: `"body_size" is possibly unbound`
  - File: `MazeGame.py` - Line 2228
  - Issue: Variable may not be defined in all code paths
  - Fix: Moved `body_size = 24` outside conditional block

- [x] **GameEntities.py Type Hint Errors**
  - Fixed: Added `Optional` type hints for functions that can return `None`
  - Fixed: Changed `direction_x` and `direction_y` from `int` to `float` in `Player.shoot()`
  - Files: `GameEntities.py`

---

## 🎮 Gameplay Enhancements

### Features to Add

- [ ] **Boss Room Improvements**
  - Add unique boss enemies
  - Boss health bar overlay
  - Boss room special music trigger
  - Boss defeat rewards

- [ ] **More Enemy Types**
  - Ranged attackers with patterns
  - Enemies that spawn minions
  - Enemies with area attacks
  - Flying enemies that avoid obstacles

- [ ] **Power-Up System**
  - Speed boost items
  - Damage multiplier items
  - Fire rate upgrades
  - Special abilities (dash, shield)

- [ ] **Room Modifiers**
  - Curse rooms (harder enemies, better loot)
  - Angel rooms (special items)
  - Challenge rooms (wave survival)
  - Shop improvements (buy items with treasure)

### Balance Tweaks

- [ ] **Review Enemy Speeds**
  - Test all enemy types for fun factor
  - Adjust difficulty curve
  - Balance shooter enemy range

- [ ] **Player Stats Review**
  - Test movement speed feel
  - Review tear speed and fire rate
  - Balance health scaling

---

## 🎨 Visual & Audio

### Visual Improvements

- [ ] **Particle Effects**
  - Bullet impact sparks
  - Enemy death particles
  - Item collection shine
  - Damage indicators (floating numbers)

- [ ] **Screen Effects**
  - Screen shake on hit
  - Flash on room clear
  - Transition effects between rooms
  - Damage vignette

- [ ] **UI Enhancements**
  - Better health display (hearts instead of numbers)
  - Minimap zoom/pan
  - Item tooltips
  - Stats display on pause

### Audio (Future)

- [ ] **Sound Effects**
  - Player shooting
  - Enemy damage/death
  - Item collection
  - Door opening/closing
  - Room clear chime

- [ ] **Music**
  - Background music system
  - Different tracks per room type
  - Boss battle music
  - Victory/defeat jingles

---

## 📝 Code Quality

### Refactoring

- [ ] **Monster AI Improvements**
  - Extract AI behaviors into separate classes
  - Make AI more modular and reusable
  - Add difficulty scaling

- [ ] **Room Generation**
  - Improve procedural generation algorithm
  - Add more room layouts
  - Better corridor connections
  - Ensure better item distribution

- [ ] **Code Organization**
  - ✓ Pixel art moved to `PixelArtAssets.py`
  - Move more visual code to separate modules
  - Create `GameEffects.py` for particles/effects
  - Create `AudioManager.py` for sounds

### Documentation

- [ ] **Code Comments**
  - Add more inline comments for complex logic
  - Document all public methods
  - Add examples to docstrings

- [ ] **User Documentation**
  - Create controls guide
  - Add strategy tips
  - Document all item types
  - Create room type guide

---

## 🧪 Testing

### Manual Testing Needed

- [ ] **Test All Room Icons**
  - Verify all icons display correctly
  - Check dimmed versions
  - Test on different backgrounds
  - Verify minimap performance

- [ ] **Gameplay Testing**
  - Test all enemy types
  - Verify room transitions
  - Check item collection
  - Test door mechanics

- [ ] **Performance Testing**
  - Check FPS with many enemies
  - Test large dungeon generation
  - Verify memory usage
  - Test long play sessions

### Automated Testing (Future)

- [ ] **Unit Tests**
  - Test pixel art rendering
  - Test collision detection
  - Test room generation
  - Test AI behavior

---

## 🚀 Future Ideas

### Long-term Goals

- [ ] **Multiple Floors**
  - Implement floor system
  - Trapdoors to next level
  - Progressive difficulty
  - Boss every X floors

- [ ] **Unlockable Content**
  - Unlockable characters
  - Unlockable items
  - Achievement system
  - Leaderboard

- [ ] **Multiplayer**
  - Local co-op
  - Shared screen
  - Independent players

- [ ] **Level Editor**
  - Custom room designer
  - Share room layouts
  - Custom challenges

---

## 📊 Priority Order

1. **URGENT**: Fix MazeGame.py errors (boss_rooms, body_size)
2. **HIGH**: Review and finalize treasure crown icon design
3. **HIGH**: Test all pixel art icons thoroughly
4. **MEDIUM**: Add more enemy types for variety
5. **MEDIUM**: Implement particle effects
6. **LOW**: Add sound effects and music
7. **FUTURE**: Multiplayer and unlockables

---

## 🔧 How to Use This TODO

1. **Before coding**: Check this file for current priorities
2. **After fixing**: Mark items as complete with `[x]`
3. **Add new tasks**: Keep this file updated with new ideas
4. **Review weekly**: Adjust priorities based on progress

---

**Last Updated**: Version 2.0 - October 2025
**Maintainer**: Pota
