import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/utils/riverpod_extensions.dart';

part 'blueprint_editor_controller.g.dart';

/// **Blueprint Editor Controller**
///
/// Manages the state of the active `render_blueprint` being edited in the GUI.
/// Strictly uses `Map<String, dynamic>` to adhere to the De-Generator Policy,
/// allowing Zero-Deploy UI structure updates.
@riverpod
class BlueprintEditorController extends _$BlueprintEditorController {
  @override
  Map<String, dynamic> build() {
    // 2. Riverpod TTL Caching (Time-To-Live for Forms)
    // Keep this form data alive for 3 minutes after the admin leaves the Studio.
    // If they navigate back within 3 minutes, they don't lose their unsaved blueprint.
    // If they take longer, Riverpod autoDisposes it to prevent stale sessions.
    ref.cacheFor(const Duration(minutes: 3));

    return {
      'version': '1.0',
      'components': [],
    };
  }

  /// Initializes the editor with an existing blueprint, or creates a clean slate.
  void initialize(Map<String, dynamic>? initialBlueprint) {
    if (initialBlueprint != null && initialBlueprint.isNotEmpty) {
      final newState = Map<String, dynamic>.from(initialBlueprint);
      if (!newState.containsKey('components')) {
        newState['components'] = [];
      }
      state = newState;
    } else {
      state = {
        'version': '1.0',
        'components': [],
      };
    }
  }

  /// Adds a new component to the end of the blueprint.
  /// Pre-fills mandatory fields to prevent Fail-Fast backend rejections.
  void addComponent(String type) {
    final components = SafeCast.safeList(state['components']);
    final newComponent = <String, dynamic>{'type': type};
    
    if (type == 'header') {
      newComponent['title'] = '';
    } else if (type == '1d_gauge') {
      newComponent['data_path'] = '\$steps.';
    } else if (type == '2d_matrix' || type == '3d_scatter') {
      newComponent['x_data_path'] = '\$steps.';
      newComponent['y_data_path'] = '\$steps.';
      if (type == '3d_scatter') {
        newComponent['z_data_path'] = '\$steps.';
      }
    } else if (type == 'evaluation_notes_panel') {
      newComponent['data_paths'] = <String>[];
    }
    
    components.add(newComponent);
    state = {...state, 'components': components};
  }

  /// Removes a component by its index.
  void removeComponent(int index) {
    final components = SafeCast.safeList(state['components']);
    if (index >= 0 && index < components.length) {
      components.removeAt(index);
      state = {...state, 'components': components};
    }
  }

  /// Updates a specific component's dictionary.
  void updateComponent(int index, Map<String, dynamic> updatedComponent) {
    final components = SafeCast.safeList(state['components']);
    if (index >= 0 && index < components.length) {
      components[index] = Map<String, dynamic>.from(updatedComponent);
      state = {...state, 'components': components};
    }
  }
  
  /// Reorders a component, supporting the Drag-and-Drop Editor interface.
  void reorderComponent(int oldIndex, int newIndex) {
    final components = SafeCast.safeList(state['components']);
    if (oldIndex < newIndex) {
      newIndex -= 1;
    }
    final item = components.removeAt(oldIndex);
    components.insert(newIndex, item);
    state = {...state, 'components': components};
  }
}
