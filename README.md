# Lanbu - Unity Android Application

A Unity-based Android application for LAN gaming and networking.

## Project Overview

Lanbu (LAN Bus) is a Unity-developed Android application that facilitates local area network gaming and communication. The app is built using Unity Engine with Kotlin for Android-specific functionality.

## Development Setup

### Prerequisites

- Unity 2022.3 LTS or later
- Android Studio
- Android SDK (API level 33+)
- JDK 11 or later
- Git

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/MillionthOdin16/Lanbu.git
   cd Lanbu
   ```

2. Open the project in Unity Hub
3. Install required packages via Package Manager
4. Configure build settings for Android
5. Build and run on device/emulator

## Project Structure

```
Lanbu/
├── Assets/                 # Unity Assets
│   ├── Scripts/           # C# Scripts
│   ├── Scenes/            # Unity Scenes
│   ├── Materials/         # Materials and Textures
│   ├── Prefabs/           # Unity Prefabs
│   └── Plugins/           # Native plugins and libraries
├── ProjectSettings/       # Unity Project Settings
├── Packages/             # Package Manager dependencies
├── android/              # Android-specific files
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/      # Kotlin/Java source
│   │   │   └── res/       # Android resources
│   │   └── build.gradle
│   ├── gradle/
│   └── build.gradle
├── build.gradle          # Root build configuration
├── gradle.properties     # Gradle properties
└── settings.gradle       # Gradle settings
```

## Features

- LAN gaming capabilities
- Network discovery and connection
- Real-time multiplayer support
- Cross-platform compatibility
- Firebase integration for analytics

## Building

### For Development
```bash
# Build for development
./gradlew assembleDebug
```

### For Release
```bash
# Build release APK
./gradlew assembleRelease
```

## Testing

```bash
# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

See [LICENSE.md](LICENSE.md) for details.

## Version History

- v0.53 - Current release with LAN gaming features