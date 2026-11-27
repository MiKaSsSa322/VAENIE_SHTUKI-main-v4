package com.frontiermilitary.item;

import com.frontiermilitary.config.FMConfig;
import com.frontiermilitary.registry.ModItems;
import com.frontiermilitary.registry.ModSounds;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** Служебный пистолет (регистрационное имя frontiermilitary:pulse_sidearm сохранено). Полуавтомат, магазин 12. */
public class ServicePistolItem extends GunItem {
    public ServicePistolItem(Properties properties) {
        super(properties, 12, 46, 6, false, 5.0F, 0.9F, 0.3F, 3.0F,
                () -> ModItems.PISTOL_AMMO.get(), () -> FMConfig.PISTOL_DAMAGE.get(), () -> ModSounds.PISTOL_SHOT.get());
        this.aimZoom = 0.9F;
        this.aimTicks = 4;
    }

    @Override
    public int modelState(ItemStack stack, long now) {
        long reload = reloadElapsed(stack, now);
        if (reload >= 0 && reload < reloadTotal(stack)) {
            if (reload < 4) return getAmmo(stack) <= 0 ? 3 : 0;
            if (reload < 7) return 4;
            if (reload < 19) return 5;
            if (reload < 23) return 6;
            if (reload < 30) return 0;
            if (reload < 35) return 7;
            if (reload < 40) return 8;
            return 0;
        }
        long shot = sinceShot(stack, now);
        if (shot == 0) return 1;
        if (shot == 1) return 2;
        return getAmmo(stack) <= 0 ? 3 : 0;
    }

    @Override
    protected void reloadSounds(Level level, Entity holder, long elapsed) {
        if (elapsed == 4) playAt(level, holder, ModSounds.MAG_OUT.get(), 0.8F, 1.0F);
        else if (elapsed == 22) playAt(level, holder, ModSounds.MAG_IN.get(), 0.8F, 1.0F);
        else if (elapsed == 30) playAt(level, holder, ModSounds.SLIDE_BACK.get(), 0.8F, 1.0F);
        else if (elapsed == 36) playAt(level, holder, ModSounds.SLIDE_FORWARD.get(), 0.9F, 1.0F);
    }

    @Override public float recoilBack() { return 0.11F; }
    @Override public float recoilPitch() { return 9.0F; }
    @Override public float cameraKick() { return 2.0F; }
}
