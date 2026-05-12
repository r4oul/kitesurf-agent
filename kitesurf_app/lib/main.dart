import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/map_screen.dart';

void main() {
  runApp(const KitesurfApp());
}

class KitesurfApp extends StatelessWidget {
  const KitesurfApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'South Coast Kitesurf',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0077B6)),
        useMaterial3: true,
      ),
      home: const MainShell(),
    );
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _tab = 0;
  String _riderLevel = 'intermediate';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0077B6),
        foregroundColor: Colors.white,
        title: const Row(
          children: [
            Text('🪁', style: TextStyle(fontSize: 20)),
            SizedBox(width: 8),
            Text('South Coast Kitesurf', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: const Color(0xFF005F92),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            child: Row(
              children: [
                const Text('I am a ', style: TextStyle(color: Colors.white70)),
                ...['beginner', 'intermediate', 'advanced'].map((level) {
                  final selected = _riderLevel == level;
                  return Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: ChoiceChip(
                      label: Text(level, style: TextStyle(
                        color: selected ? const Color(0xFF0077B6) : Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      )),
                      selected: selected,
                      selectedColor: Colors.white,
                      backgroundColor: Colors.white24,
                      onSelected: (_) => setState(() => _riderLevel = level),
                    ),
                  );
                }),
              ],
            ),
          ),
        ),
      ),
      body: IndexedStack(
        index: _tab,
        children: [
          HomeScreen(riderLevel: _riderLevel),
          MapScreen(riderLevel: _riderLevel),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.list), label: 'Beaches'),
          NavigationDestination(icon: Icon(Icons.map), label: 'Map'),
        ],
      ),
    );
  }
}
