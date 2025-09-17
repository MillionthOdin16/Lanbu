using UnityEngine;

namespace Lanbu.Core
{
    /// <summary>
    /// Main game controller for Lanbu application
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        [Header("Game Settings")]
        public string gameVersion = "0.53";
        public bool debugMode = true;
        
        [Header("Network References")]
        public Network.NetworkManager networkManager;
        
        private static GameManager instance;
        public static GameManager Instance => instance;
        
        void Awake()
        {
            // Singleton pattern
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Initialize game
            InitializeGame();
        }
        
        void Start()
        {
            Debug.Log($"Lanbu Game Manager started - Version {gameVersion}");
            
            // Find network manager if not assigned
            if (networkManager == null)
            {
                networkManager = FindObjectOfType<Network.NetworkManager>();
            }
        }
        
        private void InitializeGame()
        {
            // Set target frame rate for mobile
            Application.targetFrameRate = 60;
            
            // Don't sleep when idle
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            
            // Set quality settings for mobile
            QualitySettings.vSyncCount = 1;
            
            if (debugMode)
            {
                Debug.Log("Game initialized in debug mode");
            }
        }
        
        /// <summary>
        /// Start a new LAN game session
        /// </summary>
        public void StartLANGame()
        {
            if (networkManager != null)
            {
                networkManager.StartServer();
                Debug.Log("Started LAN game session");
            }
        }
        
        /// <summary>
        /// Join an existing LAN game
        /// </summary>
        public void JoinLANGame()
        {
            if (networkManager != null)
            {
                networkManager.StartClient();
                Debug.Log("Searching for LAN games");
            }
        }
        
        /// <summary>
        /// Exit the current game session
        /// </summary>
        public void ExitGame()
        {
            if (networkManager != null)
            {
                networkManager.StopNetworking();
            }
            
            Debug.Log("Exiting game");
            Application.Quit();
        }
        
        void OnApplicationPause(bool pauseStatus)
        {
            if (pauseStatus)
            {
                Debug.Log("Game paused");
            }
            else
            {
                Debug.Log("Game resumed");
            }
        }
        
        void OnApplicationFocus(bool hasFocus)
        {
            if (debugMode)
            {
                Debug.Log($"Game focus: {hasFocus}");
            }
        }
    }
}