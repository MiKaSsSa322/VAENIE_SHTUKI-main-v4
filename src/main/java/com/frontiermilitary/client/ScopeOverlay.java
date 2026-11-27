package com.frontiermilitary.client;

import com.frontiermilitary.FrontierMilitary;
import com.frontiermilitary.item.GunItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/** Оптический прицел: чёрные поля по бокам + круглая линза с перекрестием (текстура scope.png). */
public final class ScopeOverlay {
    private static final ResourceLocation TEXTURE = new ResourceLocation(FrontierMilitary.MODID, "textures/gui/scope.png");
    public static final IGuiOverlay OVERLAY = ScopeOverlay::render;

    private static void render(ForgeGui gui, GuiGraphics g, float partialTick, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null) {
            return;
        }
        ItemStack stack = ClientForgeEvents.heldGunStack(player);
        if (stack.isEmpty() || !((GunItem) stack.getItem()).isScoped() || ClientForgeEvents.aimProgress(partialTick) < 0.85F) {
            return;
        }
        int size = height;
        int x = (width - size) / 2;
        g.fill(0, 0, x, height, 0xFF000000);
        g.fill(x + size, 0, width, height, 0xFF000000);
        g.blit(TEXTURE, x, 0, size, size, 0.0F, 0.0F, 1024, 1024, 1024, 1024);
    }

    private ScopeOverlay() {}
}
