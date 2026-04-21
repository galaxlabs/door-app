import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:google_sign_in/google_sign_in.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthRepository {
  final FirebaseAuth _auth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  // ── Google Sign-In ──────────────────────────────────────────────────────────

  Future<UserCredential> signInWithGoogle() async {
    if (kIsWeb) {
      // Web: use Firebase popup flow
      final provider = GoogleAuthProvider();
      return _auth.signInWithPopup(provider);
    }
    // Mobile: native Google sign-in
    final account = await _googleSignIn.signIn();
    if (account == null) throw Exception('Google sign-in cancelled.');
    final googleAuth = await account.authentication;
    final credential = GoogleAuthProvider.credential(
      accessToken: googleAuth.accessToken,
      idToken: googleAuth.idToken,
    );
    return _auth.signInWithCredential(credential);
  }

  // ── Email / password ────────────────────────────────────────────────────────

  Future<UserCredential> passwordLogin({
    required String identifier,
    required String password,
  }) async {
    return _auth.signInWithEmailAndPassword(
      email: identifier.trim(),
      password: password,
    );
  }

  Future<UserCredential> register({
    required String fullName,
    required String email,
    required String phoneNumber,
    required String password,
  }) async {
    final cred = await _auth.createUserWithEmailAndPassword(
      email: email.trim(),
      password: password,
    );
    await cred.user?.updateDisplayName(fullName);
    return cred;
  }

  // ── Session ─────────────────────────────────────────────────────────────────

  Future<bool> hasSession() async {
    return _auth.currentUser != null;
  }

  User? get currentUser => _auth.currentUser;

  Stream<User?> get authStateChanges => _auth.authStateChanges();

  Future<void> logout() async {
    await _googleSignIn.signOut();
    await _auth.signOut();
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // ── Local profile draft (kept for offline guest use) ────────────────────────

  Future<Map<String, dynamic>> loadLocalProfileDraft() async {
    final user = _auth.currentUser;
    if (user != null) {
      return {
        'full_name': user.displayName ?? 'User',
        'email': user.email ?? '',
        'phone_number': user.phoneNumber ?? '',
        'photo_url': user.photoURL ?? '',
        'uid': user.uid,
        'source': 'firebase',
      };
    }
    final prefs = await SharedPreferences.getInstance();
    return {
      'full_name': prefs.getString('profile_full_name') ?? 'Guest',
      'intro': prefs.getString('profile_intro') ?? '',
      'phone_number': prefs.getString('profile_phone') ?? '',
      'email': prefs.getString('profile_email') ?? '',
      'source': 'local',
    };
  }

  Future<Map<String, dynamic>> fetchProfile() async {
    return loadLocalProfileDraft();
  }

  Future<Map<String, dynamic>> updateProfile({
    required String fullName,
    required String phoneNumber,
    required String email,
    String intro = '',
    int? age,
    String locale = 'en',
    String timezone = 'UTC',
  }) async {
    final user = _auth.currentUser;
    if (user != null && fullName.isNotEmpty) {
      await user.updateDisplayName(fullName);
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('profile_full_name', fullName);
    await prefs.setString('profile_phone', phoneNumber);
    await prefs.setString('profile_email', email);
    await prefs.setString('profile_intro', intro);
    if (age != null) await prefs.setInt('profile_age', age);
    await prefs.setString('profile_locale', locale);
    await prefs.setString('profile_timezone', timezone);
    return loadLocalProfileDraft();
  }
}
