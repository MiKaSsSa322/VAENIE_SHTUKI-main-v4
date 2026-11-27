package com.frontiermilitary.client;

import com.frontiermilitary.item.GunItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/** Счётчик патронов в правом нижнем углу, пока оружие в руках. */
public final class GunHud {
    public static final IGuiOverlay OVERLAY = GunHud::render;

    private static void render(ForgeGui gui, GuiGraphics g, float partialTick, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || mc.options.hideGui || mc.level == null) {
            return;
        }
        ItemStack stack = player.getMainHandItem().getItem() instanceof GunItem ? player.getMainHandItem()
                : (player.getOffhandItem().getItem() instanceof GunItem ? player.getOffhandItem() : ItemStack.EMPTY);
        if (stack.isEmpty()) {
            return;
        }
        GunItem gun = (GunItem) stack.getItem();

        Font font = mc.font;
        int mag = gun.magSize();
        int ammo = gun.getAmmo(stack);
        int reserve = player.getAbilities().instabuild ? -1 : gun.countAmmo(player);
        long reload = gun.reloadElapsed(stack, mc.level.getGameTime());
        boolean reloading = reload >= 0 && reload < gun.reloadTotal(stack);

        int right = width - 12;
        int y = height - 52;

        String main = String.valueOf(ammo);
        String sub = " / " + (reserve < 0 ? "\u221E" : String.valueOf(reserve));
        int mainColor = ammo <= Math.max(2, mag / 5) ? 0xFFE04030 : 0xFFF2E6B8;

        int subW = font.width(sub);
        g.drawString(font, sub, right - subW, y + 8, 0xFFA8A8A0, true);
        g.pose().pushPose();
        g.pose().translate(right - subW - font.width(main) * 2, y, 0);
        g.pose().scale(2.0F, 2.0F, 1.0F);
        g.drawString(font, main, 0, 0, mainColor, true);
        g.pose().popPose();

        // магазин в виде столбиков (для 30 патронов — тоньше)
        int step = mag > 15 ? 3 : 5;
        int barW = step - 1;
        int bx = right - mag * step;
        int by = y + 22;
        for (int i = 0; i < mag; i++) {
            int color = i < ammo ? 0xFFD8B04A : 0x55303030;
            g.fill(bx + i * step, by, bx + i * step + barW, by + 6, color);
        }

        if (reloading) {
            float p = Math.min(1.0F, reload / (float) gun.reloadTotal(stack));
            Component text = Component.translatable("hud.frontiermilitary.reloading");
            g.drawString(font, text, right - font.width(text), by + 10, 0xFFE0E0D0, true);
            g.fill(bx, by + 21, bx + mag * step - 1, by + 23, 0x66000000);
            g.fill(bx, by + 21, bx + (int) ((mag * step - 1) * p), by + 23, 0xFFD8B04A);
        }
    }

    private GunHud() {}
}
