import 'package:flutter/material.dart';

import 'colors.dart';
import 'radius.dart';
import 'typography.dart';

class AppTheme {
  /// Светлая тема приложения
  static final ThemeData light = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,

    // Цветовая схема (обновлённый синтаксис)
    colorScheme: const ColorScheme(
      brightness: Brightness.light,
      primary: AppColors.primaryLight,
      onPrimary: Colors.white,
      secondary: AppColors.secondaryLight,
      onSecondary: AppColors.foregroundLight,
      surface: AppColors.backgroundLight,
      onSurface: AppColors.foregroundLight,
      error: AppColors.destructiveLight,
      onError: Colors.white,
    ),

    scaffoldBackgroundColor: AppColors.backgroundLight,

    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.backgroundLight,
      foregroundColor: AppColors.foregroundLight,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
    ),

    textTheme: TextTheme(
      displayLarge: AppTypography.h1Light,
      displayMedium: AppTypography.h2Light,
      bodyLarge: AppTypography.bodyLight,
      labelLarge: AppTypography.labelLight,
    ),

    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primaryLight,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        minimumSize: const Size(double.infinity, 40),
        shape: RoundedRectangleBorder(borderRadius: AppRadius.circular),
        elevation: 0,
      ),
    ),

    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.secondaryLight,
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      border: OutlineInputBorder(borderRadius: AppRadius.circular, borderSide: BorderSide.none),
      focusedBorder: OutlineInputBorder(
        borderRadius: AppRadius.circular,
        borderSide: const BorderSide(color: AppColors.primaryLight, width: 1),
      ),
    ),

    cardTheme: CardThemeData(
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: AppRadius.circular,
        side: const BorderSide(color: AppColors.borderLight, width: 1),
      ),
    ),

    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: AppColors.backgroundLight,
      selectedItemColor: AppColors.primaryLight,
      unselectedItemColor: AppColors.mutedForegroundLight,
      elevation: 0,
      type: BottomNavigationBarType.fixed,
    ),
  );

  /// Тёмная тема приложения
  static final ThemeData dark = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,

    colorScheme: const ColorScheme(
      brightness: Brightness.dark,
      primary: AppColors.primaryDark,
      onPrimary: AppColors.backgroundDark,
      secondary: AppColors.secondaryDark,
      onSecondary: AppColors.foregroundDark,
      surface: AppColors.backgroundDark,
      onSurface: AppColors.foregroundDark,
      error: AppColors.destructiveDark,
      onError: AppColors.backgroundDark,
    ),

    scaffoldBackgroundColor: AppColors.backgroundDark,

    appBarTheme: const AppBarTheme(
      backgroundColor: AppColors.backgroundDark,
      foregroundColor: AppColors.foregroundDark,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
    ),

    textTheme: TextTheme(
      displayLarge: AppTypography.h1Light.copyWith(color: AppColors.foregroundDark),
      displayMedium: AppTypography.h2Light.copyWith(color: AppColors.foregroundDark),
      bodyLarge: AppTypography.bodyLight.copyWith(color: AppColors.foregroundDark),
      labelLarge: AppTypography.labelLight.copyWith(color: AppColors.foregroundDark),
    ),

    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primaryDark,
        foregroundColor: AppColors.backgroundDark,
        shape: RoundedRectangleBorder(borderRadius: AppRadius.circular),
        elevation: 0,
      ),
    ),

    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.secondaryDark,
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      border: OutlineInputBorder(borderRadius: AppRadius.circular, borderSide: BorderSide.none),
      focusedBorder: OutlineInputBorder(
        borderRadius: AppRadius.circular,
        borderSide: const BorderSide(color: AppColors.primaryDark, width: 1),
      ),
    ),

    cardTheme: CardThemeData(
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: AppRadius.circular,
        side: const BorderSide(color: AppColors.borderDark, width: 1),
      ),
    ),

    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: AppColors.backgroundDark,
      selectedItemColor: AppColors.primaryDark,
      unselectedItemColor: AppColors.mutedForegroundDark,
      elevation: 0,
      type: BottomNavigationBarType.fixed,
    ),
  );
}
