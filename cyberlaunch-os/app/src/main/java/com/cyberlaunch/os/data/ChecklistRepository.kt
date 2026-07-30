package com.cyberlaunch.os.data

import android.content.Context
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringSetPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.cyberlaunch.os.domain.ChecklistProgress
import com.cyberlaunch.os.domain.IncidentResponseChecklist
import java.io.IOException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map

private val Context.trainingDataStore by preferencesDataStore(name = "training_progress")

interface ChecklistRepository {
    val completedSteps: Flow<Set<Int>>

    suspend fun setStepCompleted(step: Int, isCompleted: Boolean)

    suspend fun reset()
}

class DataStoreChecklistRepository(
    private val context: Context,
) : ChecklistRepository {
    private val completedStepsKey = stringSetPreferencesKey("incident_response_completed_steps")

    override val completedSteps: Flow<Set<Int>> = context.trainingDataStore.data
        .catch { error ->
            if (error is IOException) {
                emit(emptyPreferences())
            } else {
                throw error
            }
        }
        .map { preferences ->
            ChecklistProgress.decode(
                stored = preferences[completedStepsKey].orEmpty(),
                stepCount = IncidentResponseChecklist.stepCount,
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

    override suspend fun reset() {
        context.trainingDataStore.edit { preferences ->
            preferences.remove(completedStepsKey)
        }
    }
}

