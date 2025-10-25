import 'package:flutter/material.dart';
import 'package:responsive_framework/responsive_framework.dart';

extension Responsive on BuildContext {
  bool get isMobileDevice => ResponsiveBreakpoints.of(this).isMobile;
  bool get isTabletDevice => ResponsiveBreakpoints.of(this).isTablet;
  bool get isDesktopDevice => ResponsiveBreakpoints.of(this).isDesktop;
}
