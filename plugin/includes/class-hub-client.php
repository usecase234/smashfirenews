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
	 * Phase 0: just enough to confirm connectivity to the Hub's /health route.
	 * Later phases add typed methods (submit(), request_draft(), rewrite(), ...)
	 * instead of a generic passthrough — mirroring the Hub's constrained
	 * action set on the plugin side too.
	 */
	public function ping(): array|WP_Error {
		if ( empty( $this->hub_url ) ) {
			return new WP_Error( 'smashfire_no_hub_url', 'SMASHFIRE_HUB_URL is not configured.' );
		}

		$response = wp_remote_request(
			trailingslashit( $this->hub_url ) . 'health',
			array(
				'method'  => 'GET',
				'timeout' => 5,
				'headers' => array(
					'Authorization' => 'Bearer ' . $this->site_credential,
				),
			)
		);

		if ( is_wp_error( $response ) ) {
			return $response;
		}

		return json_decode( wp_remote_retrieve_body( $response ), true );
	}
}
