package com.frontiermilitary.item;

import com.frontiermilitary.config.FMConfig;
import com.frontiermilitary.registry.ModItems;
import com.frontiermilitary.registry.ModSounds;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** АК-74: автоматический огонь (~600 выстр./мин), магазин 30, перезарядка со взведением затвора. */
public class Ak74Item extends GunItem {
    public Ak74Item(Properties properties) {
        super(properties, 30, 56, 2, true, 6.0F, 1.5F, 0.7F, 4.0F,
                () -> ModItems.RIFLE_AMMO.get(), () -> FMConfig.AK74_DAMAGE.get(), () -> ModSounds.RIFLE_SHOT.get());
        this.aimZoom = 0.85F;
        this.aimTicks = 6;
    }

    @Override
    public int modelState(ItemStack stack, long now) {
        long reload = reloadElapsed(stack, now);
        if (reload >= 0 && reload < reloadTotal(stack)) {
            if (reload < 4) return getAmmo(stack) <= 0 ? 3 : 0;
            if (reload < 8) return 4;
            if (reload < 24) return 5;
            if (reload < 29) return 6;
            if (reload < 34) return 0;
            if (reload < 40) return 7;
            if (reload < 46) return 8;
            return 0;
        }
        long shot = sinceShot(stack, now);
        if (shot == 0) return 1;
        if (shot == 1) return 2;
        return getAmmo(stack) <= 0 ? 3 : 0;
    }

    @Override
    protected void reloadSounds(Level level, Entity holder, long elapsed) {
        if (elapsed == 5) playAt(level, holder, ModSounds.MAG_OUT.get(), 0.9F, 0.8F);
        else if (elapsed == 28) playAt(level, holder, ModSounds.MAG_IN.get(), 0.9F, 0.8F);
        else if (elapsed == 35) playAt(level, holder, ModSounds.SLIDE_BACK.get(), 0.9F, 0.75F);
        else if (elapsed == 41) playAt(level, holder, ModSounds.SLIDE_FORWARD.get(), 1.0F, 0.75F);
    }

    @Override public float recoilBack() { return 0.07F; }
    @Override public float recoilPitch() { return 5.0F; }
    @Override public float cameraKick() { return 1.1F; }
}
