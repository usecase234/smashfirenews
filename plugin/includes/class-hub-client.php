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
	 * The single choke point for every Hub call this plugin makes. Later
	 * phases add typed methods (submit(), request_draft(), rewrite(), ...)
	 * that call through here instead of a generic passthrough — mirroring
	 * the Hub's own constrained action set on the plugin side. Nothing
	 * outside this class should call wp_remote_request() against the Hub.
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

		$decoded = json_decode( wp_remote_retrieve_body( $response ), true );

		if ( ! is_array( $decoded ) ) {
			return new WP_Error(
				'smashfire_bad_response',
				'Hub returned a non-JSON or empty response.',
				array( 'status' => wp_remote_retrieve_response_code( $response ) )
			);
		}

		return $decoded;
	}
}
