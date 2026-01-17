class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val response = findViewById<TextView>(R.id.responseText)
        val input = findViewById<EditText>(R.id.inputText)

        findViewById<Button>(R.id.sendText).setOnClickListener {
            ApiClient.sendText(input.text.toString()) {
                runOnUiThread { response.text = it }
            }
        }

        findViewById<Button>(R.id.micButton).setOnClickListener {
            startService(Intent(this, RecorderService::class.java))
        }
    }
}
