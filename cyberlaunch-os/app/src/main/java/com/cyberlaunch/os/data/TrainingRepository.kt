package com.cyberlaunch.os.data

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.cyberlaunch.os.domain.ChecklistProgress
import com.cyberlaunch.os.domain.FieldNotesPolicy
import com.cyberlaunch.os.domain.IncidentResponseChecklist
import java.io.IOException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map

private val Context.trainingDataStore by preferencesDataStore(name = "training_progress")

data class TrainingState(
    val completedSteps: Set<Int> = emptySet(),
    val fieldNotes: String = "",
    val showSafetyReminder: Boolean = true,
)

interface TrainingRepository {
    val state: Flow<TrainingState>

    suspend fun setStepCompleted(step: Int, isCompleted: Boolean)

    suspend fun resetChecklist()

    suspend fun saveFieldNotes(notes: String)

    suspend fun clearFieldNotes()

    suspend fun setShowSafetyReminder(show: Boolean)
}

class DataStoreTrainingRepository(
    private val context: Context,
) : TrainingRepository {
    private val completedStepsKey = stringSetPreferencesKey("incident_response_completed_steps")
    private val fieldNotesKey = stringPreferencesKey("field_notes")
    private val showSafetyReminderKey = booleanPreferencesKey("show_safety_reminder")

    override val state: Flow<TrainingState> = context.trainingDataStore.data
        .catch { error ->
            if (error is IOException) {
                emit(emptyPreferences())
            } else {
                throw error
            }
        }
        .map { preferences ->
            TrainingState(
                completedSteps = ChecklistProgress.decode(
                    stored = preferences[completedStepsKey].orEmpty(),
                    stepCount = IncidentResponseChecklist.stepCount,
                ),
                fieldNotes = FieldNotesPolicy.sanitize(preferences[fieldNotesKey].orEmpty()),
                showSafetyReminder = preferences[showSafetyReminderKey] ?: true,
            )
        }

    override suspend fun setStepCompleted(step: Int, isCompleted: Boolean) {
        if (step !in IncidentResponseChecklist.steps.indices) return

        context.trainingDataStore.edit { preferences ->
            val current = ChecklistProgress.decode(
                stored = preferences[completedStepsKey].orEmpty(),
                stepCount = IncidentResponseChecklist.stepCount,
            )
            val updated = ChecklistProgress.update(
                completed = current,
                step = step,
                isCompleted = isCompleted,
                stepCount = IncidentResponseChecklist.stepCount,
            )
            preferences[completedStepsKey] = ChecklistProgress.encode(
                completed = updated,
                stepCount = IncidentResponseChecklist.stepCount,
            )
        }
    }

    override suspend fun resetChecklist() {
        context.trainingDataStore.edit { preferences ->
            preferences.remove(completedStepsKey)
        }
    }

    override suspend fun saveFieldNotes(notes: String) {
        context.trainingDataStore.edit { preferences ->
            val sanitizedNotes = FieldNotesPolicy.sanitize(notes)
            if (sanitizedNotes.isEmpty()) {
                preferences.remove(fieldNotesKey)
            } else {
                preferences[fieldNotesKey] = sanitizedNotes
            }
        }
    }

    override suspend fun clearFieldNotes() {
        context.trainingDataStore.edit { preferences ->
            preferences.remove(fieldNotesKey)
        }
    }

    override suspend fun setShowSafetyReminder(show: Boolean) {
        context.trainingDataStore.edit { preferences ->
            preferences[showSafetyReminderKey] = show
        }
    }
}
