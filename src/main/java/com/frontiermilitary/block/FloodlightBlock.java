package com.frontiermilitary.block;

import net.minecraft.core.BlockPos;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;

/** Прожектор: горит (свет 15) только при питании — вплотную к работающему генератору или через силовой кабель. */
public class FloodlightBlock extends FacingBlock {
    public static final BooleanProperty LIT = BlockStateProperties.LIT;

    public FloodlightBlock(Properties properties) {
        super(properties, 3, 0, 3, 13, 16, 10);
        this.registerDefaultState(this.defaultBlockState().setValue(LIT, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, LIT);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        BlockState state = super.getStateForPlacement(context);
        return state == null ? null : state.setValue(LIT, PowerNet.isFed(context.getLevel(), context.getClickedPos()));
    }

    @Override
    @SuppressWarnings("deprecation")
    public void neighborChanged(BlockState state, Level level, BlockPos pos, Block block, BlockPos fromPos, boolean moving) {
        update(level, pos, state);
    }

    public static void update(Level level, BlockPos pos, BlockState state) {
        if (level.isClientSide) {
            return;
        }
        boolean fed = PowerNet.isFed(level, pos);
        if (fed != state.getValue(LIT)) {
            level.setBlock(pos, state.setValue(LIT, fed), 3);
        }
    }
}
