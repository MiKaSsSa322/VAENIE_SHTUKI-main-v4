package com.frontiermilitary.network;

import com.frontiermilitary.item.GunItem;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Клиент -> сервер: состояние ЛКМ (курок) и ПКМ (прицел) для оружия в руках. */
public class TriggerPacket {
    private final boolean pressed;
    private final boolean aiming;

    public TriggerPacket(boolean pressed, boolean aiming) {
        this.pressed = pressed;
        this.aiming = aiming;
    }

    public void encode(FriendlyByteBuf buf) {
        buf.writeBoolean(pressed);
        buf.writeBoolean(aiming);
    }

    public static TriggerPacket decode(FriendlyByteBuf buf) {
        return new TriggerPacket(buf.readBoolean(), buf.readBoolean());
    }

    public void handle(Supplier<NetworkEvent.Context> ctx) {
        NetworkEvent.Context context = ctx.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null) {
                return;
            }
            ItemStack main = player.getMainHandItem();
            if (main.getItem() instanceof GunItem gun) {
                gun.onTrigger(player, main, InteractionHand.MAIN_HAND, pressed, aiming);
            } else {
                ItemStack off = player.getOffhandItem();
                if (off.getItem() instanceof GunItem gun) {
                    gun.onTrigger(player, off, InteractionHand.OFF_HAND, pressed, aiming);
                }
            }
        });
        context.setPacketHandled(true);
    }
}
