package com.frontiermilitary.block;

import com.frontiermilitary.registry.ModItems;
import com.frontiermilitary.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;

/**
 * Полевой генератор: питает соседние прожекторы и силовые кабели. ПКМ канистрой с бензином — заправка (до 4 канистр, по 3 минуты работы).
 * ПКМ без канистры — завод шнуром (анимация: два рывка), затем работа и сигнал красного камня 15; ещё ПКМ — выключить.
 * stage: 0 выкл, 1/3 шнур вытянут, 2/4 шнур возвращается, 5 работает.
 */
public class GeneratorBlock extends FacingBlock {
    public static final IntegerProperty FUEL = IntegerProperty.create("fuel", 0, 4);
    public static final IntegerProperty STAGE = IntegerProperty.create("stage", 0, 5);
    private static final int FUEL_TICKS = 3600;

    public GeneratorBlock(Properties properties) {
        super(properties, 2, 0, 2, 14, 13, 14);
        this.registerDefaultState(this.defaultBlockState().setValue(FUEL, 0).setValue(STAGE, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, FUEL, STAGE);
    }

    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        ItemStack held = player.getItemInHand(hand);
        int fuel = state.getValue(FUEL);
        int stage = state.getValue(STAGE);

        if (held.is(ModItems.FUEL_CANISTER.get())) {
            if (!level.isClientSide) {
                if (fuel >= 4) {
                    player.displayClientMessage(Component.translatable("message.frontiermilitary.fuel_full"), true);
                } else {
                    level.setBlock(pos, state.setValue(FUEL, fuel + 1), 3);
                    player.setItemInHand(hand, new ItemStack(ModItems.EMPTY_CANISTER.get()));
                    level.playSound(null, pos, SoundEvents.BUCKET_EMPTY, SoundSource.BLOCKS, 1.0F, 0.8F);
                    player.displayClientMessage(Component.translatable("message.frontiermilitary.fuel_level", fuel + 1), true);
                }
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        if (!level.isClientSide) {
            if (stage == 5) {
                level.setBlock(pos, state.setValue(STAGE, 0), 3);
                PowerNet.refresh(level, pos);
                level.playSound(null, pos, SoundEvents.LEVER_CLICK, SoundSource.BLOCKS, 0.8F, 0.6F);
            } else if (stage == 0) {
                if (fuel <= 0) {
                    player.displayClientMessage(Component.translatable("message.frontiermilitary.no_fuel"), true);
                } else {
                    level.setBlock(pos, state.setValue(STAGE, 1), 3);
                    level.playSound(null, pos, ModSounds.GENERATOR_PULL.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
                    level.scheduleTick(pos, this, 4);
                }
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        int stage = state.getValue(STAGE);
        int fuel = state.getValue(FUEL);
        switch (stage) {
            case 1:
                level.setBlock(pos, state.setValue(STAGE, 2), 3);
                level.scheduleTick(pos, this, 3);
                break;
            case 2:
                level.setBlock(pos, state.setValue(STAGE, 3), 3);
                level.playSound(null, pos, ModSounds.GENERATOR_PULL.get(), SoundSource.BLOCKS, 1.0F, 1.15F);
                level.scheduleTick(pos, this, 4);
                break;
            case 3:
                level.setBlock(pos, state.setValue(STAGE, 4), 3);
                level.scheduleTick(pos, this, 3);
                break;
            case 4:
                if (fuel > 0) {
                    level.setBlock(pos, state.setValue(STAGE, 5), 3);
                    PowerNet.refresh(level, pos);
                    level.playSound(null, pos, ModSounds.GENERATOR_START.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
                    level.scheduleTick(pos, this, FUEL_TICKS);
                } else {
                    level.setBlock(pos, state.setValue(STAGE, 0), 3);
                }
                break;
            case 5:
                if (fuel <= 1) {
                    level.setBlock(pos, state.setValue(FUEL, 0).setValue(STAGE, 0), 3); // топливо кончилось
                    PowerNet.refresh(level, pos);
                    level.playSound(null, pos, SoundEvents.LEVER_CLICK, SoundSource.BLOCKS, 0.8F, 0.5F);
                } else {
                    level.setBlock(pos, state.setValue(FUEL, fuel - 1), 3);
                    level.scheduleTick(pos, this, FUEL_TICKS);
                }
                break;
            default:
                break;
        }
    }

    // ------------------------------------------------------------------ красный камень
    @Override
    @SuppressWarnings("deprecation")
    public boolean isSignalSource(BlockState state) {
        return true;
    }

    @Override
    @SuppressWarnings("deprecation")
    public int getSignal(BlockState state, BlockGetter level, BlockPos pos, Direction direction) {
        return state.getValue(STAGE) == 5 ? 15 : 0;
    }

    // ------------------------------------------------------------------ эффекты (клиент)
    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        int stage = state.getValue(STAGE);
        double x = pos.getX() + 0.5D;
        double y = pos.getY() + 0.75D;
        double z = pos.getZ() + 0.5D;
        if (stage == 5) {
            if (random.nextInt(2) == 0) {
                Direction back = state.getValue(FACING).getOpposite();
                level.addParticle(ParticleTypes.SMOKE, x + back.getStepX() * 0.28D, y, z + back.getStepZ() * 0.28D, 0.0D, 0.04D, 0.0D);
            }
            if (random.nextInt(12) == 0) {
                level.addParticle(ParticleTypes.LARGE_SMOKE, x, pos.getY() + 1.05D, z, 0.0D, 0.05D, 0.0D);
            }
            if (random.nextInt(14) == 0) {
                level.playLocalSound(x, y, z, ModSounds.GENERATOR_RUN.get(), SoundSource.BLOCKS, 0.6F, 1.0F, false);
            }
        } else if ((stage == 1 || stage == 3) && random.nextInt(2) == 0) {
            level.addParticle(ParticleTypes.SMOKE, x, y, z, 0.0D, 0.02D, 0.0D);
        }
    }
}
