import 'package:flutter/material.dart';

class AppTheme {
  static const Color _amber = Color(0xFFF6B94A);
  static const Color _teal = Color(0xFF37D6C5);
  static const Color _dark = Color(0xFF090909);
  static const Color _panel = Color(0xFF151515);
  static const Color _card = Color(0xFF1D1D1D);
  static const Color _text = Color(0xFFF7F0DC);
  static const Color _muted = Color(0xFFB8B0A0);

  static ThemeData get light => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: _amber,
          secondary: _teal,
          brightness: Brightness.light,
        ),
      );

  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: _dark,
        colorScheme: const ColorScheme.dark(
          primary: _amber,
          secondary: _teal,
          surface: _panel,
          error: Color(0xFFFF6D6D),
          onPrimary: Color(0xFF1B1406),
          onSecondary: Color(0xFF041412),
          onSurface: _text,
        ),
        cardTheme: CardThemeData(
          color: _card,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
            side: const BorderSide(color: Color(0x1FFFFFFF)),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: _card,
          labelStyle: const TextStyle(color: _muted),
          hintStyle: const TextStyle(color: _muted),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(20),
            borderSide: const BorderSide(color: Color(0x1FFFFFFF)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(20),
            borderSide: const BorderSide(color: Color(0x1FFFFFFF)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(20),
            borderSide: const BorderSide(color: _amber),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: _amber,
            foregroundColor: const Color(0xFF1B1406),
            minimumSize: const Size.fromHeight(58),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            textStyle: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 16,
            ),
          ),
        ),
        chipTheme: ChipThemeData(
          backgroundColor: const Color(0x221D1D1D),
          selectedColor: const Color(0x33F6B94A),
          side: const BorderSide(color: Color(0x1FFFFFFF)),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          labelStyle: const TextStyle(color: _text),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          foregroundColor: _text,
          centerTitle: false,
        ),
        textTheme: const TextTheme(
          headlineMedium: TextStyle(color: _text, fontWeight: FontWeight.w700),
          titleLarge: TextStyle(color: _text, fontWeight: FontWeight.w700),
          bodyLarge: TextStyle(color: _text),
          bodyMedium: TextStyle(color: _muted),
        ),
      );
}
