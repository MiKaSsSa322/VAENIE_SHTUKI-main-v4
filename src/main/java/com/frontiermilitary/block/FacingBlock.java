package com.frontiermilitary.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Блок, повёрнутый лицом к игроку. Форма задаётся для направления «север» и поворачивается автоматически. */
public class FacingBlock extends HorizontalDirectionalBlock {
    private final VoxelShape[] shapes = new VoxelShape[4];

    public FacingBlock(Properties properties, double x1, double y1, double z1, double x2, double y2, double z2) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any().setValue(FACING, Direction.NORTH));
        for (Direction d : Direction.Plane.HORIZONTAL) {
            shapes[d.get2DDataValue()] = rotated(d, x1, y1, z1, x2, y2, z2);
        }
    }

    private static VoxelShape rotated(Direction d, double x1, double y1, double z1, double x2, double y2, double z2) {
        switch (d) {
            case EAST:  return Block.box(16 - z2, y1, x1, 16 - z1, y2, x2);
            case SOUTH: return Block.box(16 - x2, y1, 16 - z2, 16 - x1, y2, 16 - z1);
            case WEST:  return Block.box(z1, y1, 16 - x2, z2, y2, 16 - x1);
            default:    return Block.box(x1, y1, z1, x2, y2, z2);
        }
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return this.defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return shapes[state.getValue(FACING).get2DDataValue()];
    }
}
