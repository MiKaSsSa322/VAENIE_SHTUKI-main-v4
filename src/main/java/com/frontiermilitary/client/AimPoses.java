package com.frontiermilitary.client;

/** Сгенерировано tools/tune_all.py: смещение камерного пространства для позы прицеливания (ADS). */
public final class AimPoses {
    private AimPoses() {}

    /** {tx, ty, tz, angleDeg, axisX, axisY, axisZ} или null. */
    public static float[] get(String itemName) {
        switch (itemName) {
            case "pulse_sidearm": return new float[]{-0.54654F, 0.21135F, -0.41742F, 18.90242F, -0.80976F, -0.58602F, 0.02939F};
            case "ak74": return new float[]{-0.71425F, 0.29534F, -0.75542F, 25.76745F, -0.60527F, -0.79542F, -0.03086F};
            case "sniper": return new float[]{-0.84961F, 0.40244F, -0.57716F, 31.18500F, -0.42656F, -0.90318F, -0.04804F};
            case "shotgun": return new float[]{-0.94966F, 0.36731F, -0.67658F, 33.46541F, -0.39630F, -0.91748F, -0.03433F};
            default: return null;
        }
    }
}
