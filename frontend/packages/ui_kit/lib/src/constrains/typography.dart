import 'package:flutter/material.dart';

import 'colors.dart';

class AppTypography {
  static const double fontSizeBase = 16.0;
  static const double lineHeight = 1.5;

  static const FontWeight fontWeightNormal = FontWeight.w400;
  static const FontWeight fontWeightMedium = FontWeight.w500;

  static TextStyle h1Light = const TextStyle(
    fontFamily: 'Inter',
    fontSize: 24,
    fontWeight: fontWeightMedium,
    height: lineHeight,
    color: AppColors.foregroundLight,
  );

  static TextStyle h2Light = const TextStyle(
    fontFamily: 'Inter',
    fontSize: 20,
    fontWeight: fontWeightMedium,
    height: lineHeight,
    color: AppColors.foregroundLight,
  );

  static TextStyle bodyLight = const TextStyle(
    fontFamily: 'Inter',
    fontSize: fontSizeBase,
    fontWeight: fontWeightNormal,
    height: lineHeight,
    color: AppColors.foregroundLight,
  );

  static TextStyle labelLight = const TextStyle(
    fontFamily: 'Inter',
    fontSize: fontSizeBase,
    fontWeight: fontWeightMedium,
    height: lineHeight,
    color: AppColors.foregroundLight,
  );
}
