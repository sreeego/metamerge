import 'dart:convert';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';

void main() {
  runApp(const GMetaMergeApp());
}

class GMetaMergeApp extends StatelessWidget {
  const GMetaMergeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'G-MetaMerge',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF1E1E2E),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF6C63FF),
        ),
      ),
      home: const HomePage(),
    );
  }
}

Future<String> extractAsset(
  String assetPath,
  String fileName,
) async {
  final appDir = await getApplicationSupportDirectory();

  final outputPath =
      '${appDir.path}${Platform.pathSeparator}$fileName';

  final outputFile = File(outputPath);

  if (!outputFile.existsSync()) {
    final data = await rootBundle.load(assetPath);

    final bytes = data.buffer.asUint8List();

    await outputFile.writeAsBytes(bytes);
  }

  return outputPath;
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() =>
      _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? inputPath;
  String? outputPath;

  bool inplaceMode = false;

  Future<void> pickInput() async {
    final path =
        await FilePicker.platform.getDirectoryPath(
          dialogTitle:
              'Select Google Takeout Folder',
        );

    if (path != null) {
      setState(() {
        inputPath = path;
      });
    }
  }

  Future<void> pickOutput() async {
    final path =
        await FilePicker.platform.getDirectoryPath(
          dialogTitle:
              'Select Output Folder',
        );

    if (path != null) {
      setState(() {
        outputPath = path;
      });
    }
  }

  Future<void> toggleInplace(
    bool value,
  ) async {
    if (!value) {
      setState(() {
        inplaceMode = false;
      });

      return;
    }

    final accepted =
        await showDialog<bool>(
          context: context,
          barrierDismissible: false,
          builder:
              (_) => const DangerDialog(),
        );

    if (accepted == true) {
      setState(() {
        inplaceMode = true;
      });
    }
  }

  void startMerge() {
    if (inputPath == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(
            const SnackBar(
              content: Text(
                'Select input folder',
              ),
            ),
          );

      return;
    }

    if (!inplaceMode &&
        outputPath == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(
            const SnackBar(
              content: Text(
                'Select output folder',
              ),
            ),
          );

      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder:
            (_) => ProcessingPage(
              inputPath: inputPath!,
              outputPath:
                  outputPath ?? '',
              inplaceMode:
                  inplaceMode,
            ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints:
              const BoxConstraints(
                maxWidth: 540,
              ),
          child: Padding(
            padding:
                const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment:
                  MainAxisAlignment.center,
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                Center(
                  child: Image.asset(
                    'assets/logo/logo.png',
                    width: 90,
                    height: 90,
                  ),
                ),

                const SizedBox(
                  height: 18,
                ),

                const Center(
                  child: Text(
                    'G-MetaMerge',
                    style: TextStyle(
                      fontSize: 38,
                      fontWeight:
                          FontWeight.bold,
                      color: Color(
                        0xFF6C63FF,
                      ),
                    ),
                  ),
                ),

                const SizedBox(
                  height: 8,
                ),

                const Center(
                  child: Text(
                    'Restore metadata from Google Photos Takeout',
                    style: TextStyle(
                      color:
                          Colors.white54,
                    ),
                  ),
                ),

                const SizedBox(
                  height: 40,
                ),

                FolderCard(
                  title: 'Input Folder',
                  path: inputPath,
                  icon:
                      Icons.folder_open,
                  onTap: pickInput,
                ),

                const SizedBox(
                  height: 16,
                ),

                if (!inplaceMode)
                  FolderCard(
                    title:
                        'Output Folder',
                    path: outputPath,
                    icon: Icons
                        .drive_folder_upload,
                    onTap:
                        pickOutput,
                  ),

                if (!inplaceMode)
                  const SizedBox(
                    height: 16,
                  ),

                Container(
                  decoration:
                      BoxDecoration(
                        color:
                            const Color(
                              0xFF2A2A3E,
                            ),
                        borderRadius:
                            BorderRadius.circular(
                              14,
                            ),
                      ),
                  child: SwitchListTile(
                    value:
                        inplaceMode,
                    activeColor:
                        Colors.redAccent,
                    onChanged:
                        toggleInplace,
                    title:
                        const Text(
                          'In-place merge mode',
                        ),
                    subtitle:
                        const Text(
                          'Modify original files directly',
                          style:
                              TextStyle(
                                color:
                                    Colors.white54,
                              ),
                        ),
                  ),
                ),

                const SizedBox(
                  height: 40,
                ),

                SizedBox(
                  width:
                      double.infinity,
                  height: 52,
                  child:
                      ElevatedButton(
                        onPressed:
                            startMerge,
                        style: ElevatedButton.styleFrom(
                          backgroundColor:
                              const Color(
                                0xFF6C63FF,
                              ),
                          foregroundColor:
                              Colors.white,
                          shape:
                              RoundedRectangleBorder(
                                borderRadius:
                                    BorderRadius.circular(
                                      14,
                                    ),
                              ),
                        ),
                        child:
                            const Text(
                              'Start Merge',
                              style:
                                  TextStyle(
                                    fontSize:
                                        16,
                                    fontWeight:
                                        FontWeight.bold,
                                  ),
                            ),
                      ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class DangerDialog
    extends StatefulWidget {
  const DangerDialog({
    super.key,
  });

  @override
  State<DangerDialog>
  createState() =>
      _DangerDialogState();
}

class _DangerDialogState
    extends State<DangerDialog>
    with
        SingleTickerProviderStateMixin {
  late AnimationController
  controller;

  @override
  void initState() {
    super.initState();

    controller = AnimationController(
      vsync: this,
      duration:
          const Duration(seconds: 1),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (_, __) {
        return AlertDialog(
          backgroundColor:
              Color.lerp(
                const Color(
                  0xFF3A0D0D,
                ),
                const Color(
                  0xFF7A1010,
                ),
                controller.value,
              ),
          shape:
              RoundedRectangleBorder(
                borderRadius:
                    BorderRadius.circular(
                      18,
                    ),
              ),
          title: const Row(
            children: [
              Icon(
                Icons.warning_rounded,
                color:
                    Colors.redAccent,
              ),
              SizedBox(width: 12),
              Text(
                'Dangerous Mode',
              ),
            ],
          ),
          content: const Column(
            mainAxisSize:
                MainAxisSize.min,
            crossAxisAlignment:
                CrossAxisAlignment.start,
            children: [
              Text(
                'This mode modifies your original files directly.',
                style: TextStyle(
                  fontWeight:
                      FontWeight.w600,
                ),
              ),

              SizedBox(height: 16),

              Text(
                'RISKS:',
                style: TextStyle(
                  color:
                      Colors.amberAccent,
                  fontWeight:
                      FontWeight.bold,
                ),
              ),

              SizedBox(height: 8),

              Text(
                '• Original files may become corrupted\n'
                '• Interrupted processing can damage media\n'
                '• Metadata overwrite cannot be undone\n'
                '• Existing metadata may be lost\n'
                '• Corresponding JSON files will be deleted\n'
                '• Backups are strongly recommended',
                style: TextStyle(
                  color:
                      Colors.amber,
                  height: 1.5,
                  fontWeight:
                      FontWeight.w600,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(
                  context,
                  false,
                );
              },
              child: const Text(
                'Cancel',
              ),
            ),

            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor:
                    Colors.redAccent,
              ),
              onPressed: () {
                Navigator.pop(
                  context,
                  true,
                );
              },
              child: const Text(
                'I Understand',
              ),
            ),
          ],
        );
      },
    );
  }
}

class FolderCard
    extends StatelessWidget {
  final String title;
  final String? path;
  final IconData icon;
  final VoidCallback onTap;

  const FolderCard({
    super.key,
    required this.title,
    required this.path,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius:
          BorderRadius.circular(14),
      onTap: onTap,
      child: Container(
        padding:
            const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color:
              const Color(0xFF2A2A3E),
          borderRadius:
              BorderRadius.circular(
                14,
              ),
          border: Border.all(
            color:
                path != null
                ? const Color(
                    0xFF6C63FF,
                  )
                : Colors.white12,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color:
                  path != null
                  ? const Color(
                      0xFF6C63FF,
                    )
                  : Colors.white38,
            ),

            const SizedBox(width: 16),

            Expanded(
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style:
                        const TextStyle(
                          color:
                              Colors
                                  .white54,
                          fontSize:
                              12,
                        ),
                  ),

                  const SizedBox(
                    height: 4,
                  ),

                  Text(
                    path ??
                        'Not selected',
                    overflow:
                        TextOverflow
                            .ellipsis,
                    style: TextStyle(
                      color:
                          path != null
                          ? Colors
                                .white
                          : Colors
                                .white38,
                    ),
                  ),
                ],
              ),
            ),

            const Icon(
              Icons.chevron_right,
              color:
                  Colors.white24,
            ),
          ],
        ),
      ),
    );
  }
}

class ProcessingPage
    extends StatefulWidget {
  final String inputPath;
  final String outputPath;
  final bool inplaceMode;

  const ProcessingPage({
    super.key,
    required this.inputPath,
    required this.outputPath,
    required this.inplaceMode,
  });

  @override
  State<ProcessingPage>
  createState() =>
      _ProcessingPageState();
}

class _ProcessingPageState
    extends State<ProcessingPage> {
  final List<String> logs = [];

  bool running = true;

  int merged = 0;
  int noSidecar = 0;
  int errors = 0;

  @override
  void initState() {
    super.initState();
    runMerge();
  }

  Future<void> runMerge() async {
    final backendExe =
        await extractAsset(
          'assets/backend/g_metamerge.exe',
          'g_metamerge.exe',
        );

    final ffmpegExe =
        await extractAsset(
          'assets/ffmpeg/ffmpeg.exe',
          'ffmpeg.exe',
        );

    setState(() {
      logs.add(
        '🚀 Starting G-MetaMerge...',
      );

      logs.add(
        '⚙️ Using embedded backend',
      );
    });

    final args = [
      '--input',
      widget.inputPath,
    ];

    if (!widget.inplaceMode) {
      args.addAll([
        '--output',
        widget.outputPath,
      ]);
    }

    if (widget.inplaceMode) {
      args.add('--inplace');
    }

    final process =
        await Process.start(
          backendExe,
          args,
          runInShell: true,
          environment: {
            'PYTHONUTF8': '1',
            'FFMPEG_PATH':
                ffmpegExe,
          },
        );

    process.stdout
        .transform(utf8.decoder)
        .listen((chunk) {
          final lines =
              chunk.split('\n');

          for (final line
              in lines) {
            final l =
                line.trim();

            if (l.isEmpty) {
              continue;
            }

            setState(() {
              logs.add(l);

              final mergedMatch =
                  RegExp(
                    r'^✅ Merged:\s+(\d+)',
                  ).firstMatch(l);

              if (mergedMatch !=
                  null) {
                merged = int.parse(
                  mergedMatch.group(
                    1,
                  )!,
                );
              }

              final noSidecarMatch =
                  RegExp(
                    r'^⚠️ No sidecar:\s+(\d+)',
                  ).firstMatch(l);

              if (noSidecarMatch !=
                  null) {
                noSidecar =
                    int.parse(
                      noSidecarMatch
                          .group(
                            1,
                          )!,
                    );
              }

              final errorsMatch =
                  RegExp(
                    r'^❌ Errors:\s+(\d+)',
                  ).firstMatch(l);

              if (errorsMatch !=
                  null) {
                errors = int.parse(
                  errorsMatch.group(
                    1,
                  )!,
                );
              }
            });
          }
        });

    process.stderr
        .transform(utf8.decoder)
        .listen((chunk) {
          final lines =
              chunk.split('\n');

          for (final line
              in lines) {
            final l =
                line.trim();

            if (l.isEmpty) {
              continue;
            }

            setState(() {
              logs.add(
                'ERR: $l',
              );
            });
          }
        });

    final exitCode =
        await process.exitCode;

    await Future.delayed(
      const Duration(
        milliseconds: 300,
      ),
    );

    String? savedLogPath;

    try {
      final timestamp =
          DateTime.now()
              .toIso8601String()
              .replaceAll(
                ':',
                '-',
              );

      final logDirectory =
          widget.inplaceMode
          ? widget.inputPath
          : widget.outputPath;

      final logFile = File(
        '$logDirectory${Platform.pathSeparator}'
        'g_metamerge_log_$timestamp.txt',
      );

      await logFile
          .writeAsString(
            logs.join('\n'),
          );

      savedLogPath =
          logFile.path;
    } catch (_) {}

    setState(() {
      logs.add(
        '🏁 Process exited with code $exitCode',
      );

      if (savedLogPath !=
          null) {
        logs.add(
          '📄 Log saved to:',
        );

        logs.add(
          savedLogPath!,
        );
      }

      running = false;
    });
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    return Scaffold(
      body: Padding(
        padding:
            const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (running)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child:
                        CircularProgressIndicator(
                          strokeWidth:
                              2,
                          color: Color(
                            0xFF6C63FF,
                          ),
                        ),
                  ),

                const SizedBox(
                  width: 12,
                ),

                Text(
                  running
                      ? 'Processing...'
                      : 'Done!',
                  style:
                      const TextStyle(
                        fontSize: 28,
                        fontWeight:
                            FontWeight.bold,
                      ),
                ),
              ],
            ),

            const SizedBox(
              height: 8,
            ),

            if (!running)
              Row(
                children: [
                  StatCard(
                    title:
                        'Merged',
                    value:
                        merged,
                    color:
                        const Color(
                          0xFF6C63FF,
                        ),
                  ),

                  const SizedBox(
                    width: 16,
                  ),

                  StatCard(
                    title:
                        'No sidecar',
                    value:
                        noSidecar,
                    color:
                        Colors.orange,
                  ),

                  const SizedBox(
                    width: 16,
                  ),

                  StatCard(
                    title:
                        'Errors',
                    value:
                        errors,
                    color:
                        Colors
                            .redAccent,
                  ),
                ],
              ),

            const SizedBox(
              height: 24,
            ),

            Expanded(
              child: Container(
                padding:
                    const EdgeInsets.all(
                      16,
                    ),
                decoration:
                    BoxDecoration(
                      color:
                          const Color(
                            0xFF2A2A3E,
                          ),
                      borderRadius:
                          BorderRadius.circular(
                            14,
                          ),
                    ),
                child:
                    ListView.builder(
                      itemCount:
                          logs.length,
                      itemBuilder:
                          (_, i) {
                            final log =
                                logs[i];

                            return Padding(
                              padding:
                                  const EdgeInsets.symmetric(
                                    vertical:
                                        2,
                                  ),
                              child: Text(
                                log,
                                style: TextStyle(
                                  fontFamily:
                                      'monospace',
                                  fontSize:
                                      13,
                                  color:
                                      log.startsWith(
                                            '❌',
                                          )
                                      ? Colors.redAccent
                                      : log.startsWith(
                                            '⚠️',
                                          )
                                      ? Colors.orange
                                      : log.startsWith(
                                            '✅',
                                          )
                                      ? Colors.greenAccent
                                      : Colors.white70,
                                ),
                              ),
                            );
                          },
                    ),
              ),
            ),

            if (!running) ...[
              const SizedBox(
                height: 24,
              ),

              Row(
                children: [
                  Expanded(
                    child: SizedBox(
                      height: 52,
                      child:
                          ElevatedButton.icon(
                            onPressed:
                                () async {
                                  await Clipboard.setData(
                                    ClipboardData(
                                      text: logs.join(
                                        '\n',
                                      ),
                                    ),
                                  );

                                  if (!context
                                      .mounted) {
                                    return;
                                  }

                                  ScaffoldMessenger.of(
                                    context,
                                  ).showSnackBar(
                                    const SnackBar(
                                      content:
                                          Text(
                                            'Logs copied to clipboard',
                                          ),
                                    ),
                                  );
                                },
                            icon:
                                const Icon(
                                  Icons.copy,
                                ),
                            label:
                                const Text(
                                  'Copy Logs',
                                ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  const Color(
                                    0xFF3A3A50,
                                  ),
                            ),
                          ),
                    ),
                  ),

                  const SizedBox(
                    width: 16,
                  ),

                  Expanded(
                    child: SizedBox(
                      height: 52,
                      child:
                          ElevatedButton(
                            onPressed:
                                () {
                                  Navigator.pop(
                                    context,
                                  );
                                },
                            style: ElevatedButton.styleFrom(
                              backgroundColor:
                                  const Color(
                                    0xFF2A2A3E,
                                  ),
                            ),
                            child:
                                const Text(
                                  'Back',
                                ),
                          ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class StatCard
    extends StatelessWidget {
  final String title;
  final int value;
  final Color color;

  const StatCard({
    super.key,
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(
    BuildContext context,
  ) {
    return Container(
      padding:
          const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 10,
          ),
      decoration: BoxDecoration(
        color:
            color.withOpacity(0.12),
        borderRadius:
            BorderRadius.circular(
              12,
            ),
        border: Border.all(
          color:
              color.withOpacity(
                0.3,
              ),
        ),
      ),
      child: Column(
        children: [
          Text(
            '$value',
            style: TextStyle(
              color: color,
              fontSize: 20,
              fontWeight:
                  FontWeight.bold,
            ),
          ),

          Text(
            title,
            style:
                const TextStyle(
                  color:
                      Colors.white54,
                  fontSize: 11,
                ),
          ),
        ],
      ),
    );
  }
}