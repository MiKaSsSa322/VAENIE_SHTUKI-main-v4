package com.frontiermilitary.block;

import com.frontiermilitary.registry.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;

/** Топливная бочка: хранит до 4 заправок. ПКМ пустой канистрой — набрать, полной — долить обратно. */
public class FuelDrumBlock extends ShapedBlock {
    public static final IntegerProperty FUEL = IntegerProperty.create("fuel", 0, 4);

    public FuelDrumBlock(Properties properties) {
        super(properties, 3, 0, 3, 13, 14, 13);
        this.registerDefaultState(this.stateDefinition.any().setValue(FUEL, 4));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FUEL);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        ItemStack held = player.getItemInHand(hand);
        int fuel = state.getValue(FUEL);

        if (held.is(ModItems.EMPTY_CANISTER.get())) {
            if (fuel <= 0) {
                if (!level.isClientSide) {
                    player.displayClientMessage(Component.translatable("message.frontiermilitary.drum_empty"), true);
                }
            } else if (!level.isClientSide) {
                level.setBlock(pos, state.setValue(FUEL, fuel - 1), 3);
                player.setItemInHand(hand, new ItemStack(ModItems.FUEL_CANISTER.get()));
                level.playSound(null, pos, SoundEvents.BUCKET_FILL, SoundSource.BLOCKS, 1.0F, 0.9F);
                player.displayClientMessage(Component.translatable("message.frontiermilitary.drum_level", fuel - 1), true);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        if (held.is(ModItems.FUEL_CANISTER.get())) {
            if (fuel < 4 && !level.isClientSide) {
                level.setBlock(pos, state.setValue(FUEL, fuel + 1), 3);
                player.setItemInHand(hand, new ItemStack(ModItems.EMPTY_CANISTER.get()));
                level.playSound(null, pos, SoundEvents.BUCKET_EMPTY, SoundSource.BLOCKS, 1.0F, 0.9F);
                player.displayClientMessage(Component.translatable("message.frontiermilitary.drum_level", fuel + 1), true);
            } else if (fuel >= 4 && !level.isClientSide) {
                player.displayClientMessage(Component.translatable("message.frontiermilitary.fuel_full"), true);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        if (!level.isClientSide) {
            player.displayClientMessage(Component.translatable("message.frontiermilitary.drum_level", fuel), true);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
}
