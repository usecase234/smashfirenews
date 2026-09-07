<?php
/**
 * Admin-facing REST proxy for the Incoming/Drafts screens.
 *
 * Every route here just forwards to a typed Smashfire_Hub_Client method and
 * relays its result — no business logic, no direct wp_remote_request. The
 * one exception is `publish`, which also has to do actual WordPress work
 * (create the post) that only this side of the system can do; see
 * Smashfire_PR_Publisher for that.
 *
 * All routes require `edit_posts`, the same capability the admin menu pages
 * already require (see class-admin-menu.php) — this is an internal editorial
 * tool, not the public submission endpoint.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_PR_Rest_Routes {

	public const REST_NAMESPACE = 'smashfire-pr/v1';

	public static function register(): void {
		add_action( 'rest_api_init', array( __CLASS__, 'register_routes' ) );
	}

	public static function register_routes(): void {
		register_rest_route(
			self::REST_NAMESPACE,
			'/queue',
			array(
				'methods'             => 'GET',
				'permission_callback' => array( __CLASS__, 'check_permission' ),
				'callback'            => array( __CLASS__, 'get_queue' ),
			)
		);

		register_rest_route(
			self::REST_NAMESPACE,
			'/drafts',
			array(
				'methods'             => 'GET',
				'permission_callback' => array( __CLASS__, 'check_permission' ),
				'callback'            => array( __CLASS__, 'get_drafts' ),
			)
		);

		register_rest_route(
			self::REST_NAMESPACE,
			'/submissions/(?P<id>\d+)/generate-draft',
			array(
				'methods'             => 'POST',
				'permission_callback' => array( __CLASS__, 'check_permission' ),
				'callback'            => array( __CLASS__, 'generate_draft' ),
			)
		);

		register_rest_route(
			self::REST_NAMESPACE,
			'/submissions/(?P<id>\d+)/publish',
			array(
				'methods'             => 'POST',
				'permission_callback' => array( __CLASS__, 'check_permission' ),
				'callback'            => array( __CLASS__, 'publish' ),
			)
		);
	}

	public static function check_permission(): bool {
		return current_user_can( 'edit_posts' );
	}

	public static function get_queue(): WP_REST_Response {
		return self::relay( ( new Smashfire_Hub_Client() )->list_queue() );
	}

	public static function get_drafts(): WP_REST_Response {
		return self::relay( ( new Smashfire_Hub_Client() )->list_drafts() );
	}

	public static function generate_draft( WP_REST_Request $request ): WP_REST_Response {
		$submission_id = (int) $request->get_param( 'id' );
		return self::relay( ( new Smashfire_Hub_Client() )->generate_draft( $submission_id ) );
	}

	public static function publish( WP_REST_Request $request ): WP_REST_Response {
		$submission_id = (int) $request->get_param( 'id' );
		$result        = Smashfire_PR_Publisher::publish_submission( $submission_id );
		return self::relay( $result );
	}

	/**
	 * Turns a Hub_Client result (array on success, WP_Error on failure)
	 * into a REST response, without leaking Hub-internal error detail
	 * beyond a message an editor can act on.
	 */
	private static function relay( array|WP_Error $result ): WP_REST_Response {
		if ( is_wp_error( $result ) ) {
			$status = (int) ( $result->get_error_data()['status'] ?? 502 );
			return new WP_REST_Response(
				array( 'error' => $result->get_error_message() ),
				$status >= 400 ? $status : 502
			);
		}
		return new WP_REST_Response( $result, 200 );
	}
}
