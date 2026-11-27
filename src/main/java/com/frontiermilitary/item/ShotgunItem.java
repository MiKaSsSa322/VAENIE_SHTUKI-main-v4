package com.frontiermilitary.item;

import com.frontiermilitary.config.FMConfig;
import com.frontiermilitary.registry.ModItems;
import com.frontiermilitary.registry.ModSounds;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Помповый дробовик: 5 патронов, 8 дробин за выстрел, патроны заряжаются по одному, помпа после выстрела. */
public class ShotgunItem extends GunItem {
    public ShotgunItem(Properties properties) {
        super(properties, 5, 0, 16, false, 4.5F, 5.0F, 4.0F, 7.0F,
                () -> ModItems.SHOTGUN_SHELLS.get(), () -> FMConfig.SHOTGUN_PELLET_DAMAGE.get(), () -> ModSounds.SHOTGUN_SHOT.get());
        this.pellets = 8;
        this.perShell = true;
        this.bulletLife = 14;
        this.bulletGravity = 0.012D;
        this.headshot = 1.2F;
        this.aimSpreadFactor = 0.6F;
        this.aimZoom = 0.88F;
        this.aimTicks = 6;
    }

    @Override
    public int modelState(ItemStack stack, long now) {
        long reload = reloadElapsed(stack, now);
        if (reload >= 0 && reload < reloadTotal(stack)) {
            if (reload < shellSetup) return 0;
            long phase = (reload - shellSetup) % shellTicks;
            if (phase < 4) return 4;
            if (phase < 8) return 6;
            return 0;
        }
        long shot = sinceShot(stack, now);
        if (shot == 0) return 1;
        if (shot >= 6 && shot < 12) return 7;
        if (shot >= 12 && shot < 18) return 8;
        return 0;
    }

    @Override
    protected void postShot(Level level, Entity holder, long since) {
        if (since == 6) playAt(level, holder, ModSounds.SHOTGUN_PUMP.get(), 0.9F, 0.9F);
        else if (since == 12) playAt(level, holder, ModSounds.SHOTGUN_PUMP.get(), 0.9F, 1.1F);
    }

    @Override
    protected void reloadSounds(Level level, Entity holder, long elapsed) {
        // звуки досылания патронов обрабатываются в GunItem.inventoryTick
    }

    @Override public float recoilBack() { return 0.14F; }
    @Override public float recoilPitch() { return 11.0F; }
    @Override public float cameraKick() { return 3.5F; }
}
