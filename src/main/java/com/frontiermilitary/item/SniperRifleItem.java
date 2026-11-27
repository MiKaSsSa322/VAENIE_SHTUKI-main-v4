package com.frontiermilitary.item;

import com.frontiermilitary.config.FMConfig;
import com.frontiermilitary.registry.ModItems;
import com.frontiermilitary.registry.ModSounds;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Снайперская винтовка: затворная, магазин 5, оптический прицел (ПКМ), большой урон, цикл затвора после выстрела. */
public class SniperRifleItem extends GunItem {
    public SniperRifleItem(Properties properties) {
        super(properties, 5, 70, 24, false, 12.0F, 6.0F, 3.0F, 10.0F,
                () -> ModItems.SNIPER_AMMO.get(), () -> FMConfig.SNIPER_DAMAGE.get(), () -> ModSounds.SNIPER_SHOT.get());
        this.aimSpreadFactor = 0.0F;   // с прицелом пуля летит точно в перекрестие
        this.aimZoom = 0.2F;
        this.scoped = true;
        this.aimTicks = 8;
        this.bulletLife = 60;
        this.bulletGravity = 0.002D;
        this.headshot = 2.5F;
    }

    @Override
    public int modelState(ItemStack stack, long now) {
        long reload = reloadElapsed(stack, now);
        if (reload >= 0 && reload < reloadTotal(stack)) {
            if (reload < 4) return 0;
            if (reload < 9) return 4;
            if (reload < 30) return 5;
            if (reload < 36) return 6;
            if (reload < 42) return 0;
            if (reload < 48) return 7;
            if (reload < 54) return 8;
            return 0;
        }
        long shot = sinceShot(stack, now);
        if (shot == 0) return 1;
        if (shot >= 8 && shot < 14) return 7;
        if (shot >= 14 && shot < 20) return 8;
        return 0;
    }

    @Override
    protected void postShot(Level level, Entity holder, long since) {
        if (since == 8) playAt(level, holder, ModSounds.SLIDE_BACK.get(), 0.9F, 0.7F);
        else if (since == 14) playAt(level, holder, ModSounds.SLIDE_FORWARD.get(), 1.0F, 0.7F);
    }

    @Override
    protected void reloadSounds(Level level, Entity holder, long elapsed) {
        if (elapsed == 5) playAt(level, holder, ModSounds.MAG_OUT.get(), 0.9F, 0.75F);
        else if (elapsed == 34) playAt(level, holder, ModSounds.MAG_IN.get(), 0.9F, 0.75F);
        else if (elapsed == 43) playAt(level, holder, ModSounds.SLIDE_BACK.get(), 0.9F, 0.7F);
        else if (elapsed == 49) playAt(level, holder, ModSounds.SLIDE_FORWARD.get(), 1.0F, 0.7F);
    }

    @Override public float recoilBack() { return 0.18F; }
    @Override public float recoilPitch() { return 14.0F; }
    @Override public float cameraKick() { return 6.0F; }
}
