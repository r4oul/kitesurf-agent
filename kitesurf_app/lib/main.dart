import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/map_screen.dart';
import 'widgets/ckite_icon.dart';
import 'theme.dart';

void main() {
  runApp(const KitesurfApp());
}

class KitesurfApp extends StatelessWidget {
  const KitesurfApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'South West Kitesurf',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(),
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
        backgroundColor: kAppBarColor,
        foregroundColor: kTextPrimary,
        elevation: 0,
        title: const Row(
          children: [
            CKiteIcon(size: 28, color: kAccent),
            SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('South West Kitesurf',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: kTextPrimary)),
                Text('Developed by Kitesurfers for Kitesurfers',
                    style: TextStyle(fontSize: 10, color: kTextSecondary, fontWeight: FontWeight.normal)),
              ],
            ),
          ],
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: kAppBarBottom,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            child: Row(
              children: [
                const Text('I am a ', style: TextStyle(color: kTextSecondary)),
                ...['beginner', 'intermediate', 'advanced'].map((level) {
                  final selected = _riderLevel == level;
                  return Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: ChoiceChip(
                      label: Text(level,
                          style: TextStyle(
                            color: selected ? kChipSelectedText : kTextSecondary,
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                          )),
                      selected: selected,
                      selectedColor: kChipSelected,
                      backgroundColor: kChipUnselected,
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
