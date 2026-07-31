package com.cyberlaunch.os

import androidx.compose.ui.test.ExperimentalTestApi
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.assertIsOff
import androidx.compose.ui.test.assertIsOn
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.isOff
import androidx.compose.ui.test.junit4.v2.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.cyberlaunch.os.data.DataStoreTrainingRepository
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
@OptIn(ExperimentalTestApi::class)
class LocalPersistenceTest {
    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    private val repository by lazy {
        DataStoreTrainingRepository(
            InstrumentationRegistry.getInstrumentation().targetContext.applicationContext,
        )
    }

    @Before
    fun resetSavedTrainingState() {
        runBlocking {
            repository.clearFieldNotes()
            repository.setShowSafetyReminder(true)
        }
    }

    @After
    fun restoreSafetyReminder() {
        runBlocking {
            repository.setShowSafetyReminder(true)
        }
    }

    @Test
    fun savedNoteSurvivesActivityRecreationAndCanBeCleared() {
        composeRule.onNodeWithText("Field Notes")
            .performScrollTo()
            .performClick()

        composeRule.onNodeWithText("Training notes")
            .performTextInput("dnsnote")
        composeRule.onNodeWithText("Unsaved changes")
            .assertIsDisplayed()

        composeRule.onNodeWithText("Save notes")
            .performClick()
        composeRule.waitUntilExactlyOneExists(
            matcher = hasText("Saved locally"),
            timeoutMillis = 5_000,
        )

        composeRule.activityRule.scenario.recreate()

        composeRule.onNodeWithText("Training notes")
            .assertTextContains("dnsnote")
        composeRule.onNodeWithText("Clear")
            .performClick()
        composeRule.onNodeWithText("Clear notes")
            .performClick()
        composeRule.onNodeWithText("0/4000")
            .assertIsDisplayed()
    }

    @Test
    fun safetyReminderSettingSurvivesActivityRecreation() {
        composeRule.onNodeWithText("AUTHORIZED LAB USE ONLY")
            .assertIsDisplayed()

        composeRule.onNodeWithText("Settings")
            .performScrollTo()
            .performClick()
        composeRule.onNodeWithText("Show safety reminder")
            .assertIsOn()
            .performClick()
        composeRule.waitUntilExactlyOneExists(
            matcher = hasText("Show safety reminder") and isOff(),
            timeoutMillis = 5_000,
        )

        composeRule.activityRule.scenario.recreate()

        composeRule.waitUntilExactlyOneExists(
            matcher = hasText("Show safety reminder") and isOff(),
            timeoutMillis = 5_000,
        )
        composeRule.onNodeWithContentDescription("Back")
            .performClick()
        composeRule.onAllNodesWithText("AUTHORIZED LAB USE ONLY")
            .assertCountEquals(0)
    }
}
