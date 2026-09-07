<?php
/**
 * The plugin's only channel to the Hub. All Hub calls go through
 * wp_remote_request with the signed per-installation site credential —
 * this class never sees or forwards an LLM provider key.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_Hub_Client {

	private string $hub_url;
	private string $site_credential;

	public function __construct() {
		$this->hub_url         = defined( 'SMASHFIRE_HUB_URL' ) ? SMASHFIRE_HUB_URL : '';
		$this->site_credential = defined( 'SMASHFIRE_SITE_CREDENTIAL' ) ? SMASHFIRE_SITE_CREDENTIAL : '';
	}

	/**
	 * Confirms connectivity to the Hub's /health route.
	 */
	public function ping(): array|WP_Error {
		return $this->request( 'GET', 'health' );
	}

	/**
	 * Phase 3: intake a publicist's submission. The original text/contact
	 * details are stored immutably on the Hub — this plugin never edits
	 * them afterward.
	 */
	public function submit_release( array $payload ): array|WP_Error {
		return $this->request( 'POST', 'submissions', $payload );
	}

	/**
	 * Pre-Writer queue: submissions with no draft generated yet.
	 */
	public function list_queue(): array|WP_Error {
		return $this->request( 'GET', 'submissions?status=queued' );
	}

	/**
	 * Finished Drafts: submissions with at least one generated draft,
	 * not yet published.
	 */
	public function list_drafts(): array|WP_Error {
		return $this->request( 'GET', 'submissions?status=drafted' );
	}

	/**
	 * Full detail for one submission, including its draft versions —
	 * used to pull the latest draft body when the editor publishes.
	 */
	public function get_submission( int $submission_id ): array|WP_Error {
		return $this->request( 'GET', "submissions/{$submission_id}" );
	}

	/**
	 * Runs the Hub's `generate_publisher_draft` action (Phase 3: a stub
	 * that echoes the original text back as Draft V1). Never a raw prompt
	 * — this plugin only ever invokes the Hub's named actions.
	 */
	public function generate_draft( int $submission_id ): array|WP_Error {
		return $this->request( 'POST', "submissions/{$submission_id}/generate-draft" );
	}

	/**
	 * Records provenance on the Hub once this plugin has actually created
	 * the WordPress post — the Hub never creates that post itself.
	 */
	public function mark_published( int $submission_id, int $wp_post_id, string $live_url ): array|WP_Error {
		return $this->request(
			'POST',
			"submissions/{$submission_id}/publish",
			array(
				'wp_post_id' => $wp_post_id,
				'live_url'   => $live_url,
			)
		);
	}

	/**
	 * The single choke point for every Hub call this plugin makes. Typed
	 * methods above call through here instead of a generic passthrough —
	 * mirroring the Hub's own constrained action set on the plugin side.
	 * Nothing outside this class should call wp_remote_request() against
	 * the Hub.
	 */
	private function request( string $method, string $path, ?array $body = null ): array|WP_Error {
		if ( empty( $this->hub_url ) ) {
			return new WP_Error( 'smashfire_no_hub_url', 'SMASHFIRE_HUB_URL is not configured.' );
		}

		$args = array(
			'method'  => $method,
			'timeout' => 5,
			'headers' => array(
				'Authorization' => 'Bearer ' . $this->site_credential,
			),
		);

		if ( null !== $body ) {
			$args['headers']['Content-Type'] = 'application/json';
			$args['body']                    = wp_json_encode( $body );
		}

		$response = wp_remote_request( trailingslashit( $this->hub_url ) . $path, $args );

		if ( is_wp_error( $response ) ) {
			return $response;
		}

		$status  = wp_remote_retrieve_response_code( $response );
		$decoded = json_decode( wp_remote_retrieve_body( $response ), true );

		if ( ! is_array( $decoded ) ) {
			return new WP_Error(
				'smashfire_bad_response',
				'Hub returned a non-JSON or empty response.',
				array( 'status' => $status )
			);
		}

		if ( $status >= 400 ) {
			return new WP_Error(
				'smashfire_hub_error',
				is_string( $decoded['detail'] ?? null ) ? $decoded['detail'] : 'The Hub rejected the request.',
				array( 'status' => $status )
			);
		}

		return $decoded;
	}
}
