<?php
/**
 * The one thing in this plugin that isn't a Hub proxy: turning an
 * editor-approved Hub draft into a real WordPress post.
 *
 * Per the source plan's editor workflow step 7, publishing creates/updates
 * a normal WordPress post and "retains source provenance privately" — so
 * provenance goes into underscore-prefixed postmeta, which WordPress hides
 * from the Custom Fields UI and excludes from the REST API response by
 * default, rather than into post content or a public field.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_PR_Publisher {

	/**
	 * Fetches the submission's latest draft from the Hub, creates a
	 * WordPress post from it, and reports the resulting post back to the
	 * Hub so it can record publish provenance.
	 *
	 * Returns the Hub's post-publish submission record on success (which
	 * is what the admin UI displays), or a WP_Error on any failure.
	 */
	public static function publish_submission( int $submission_id ): array|WP_Error {
		$hub = new Smashfire_Hub_Client();

		$submission = $hub->get_submission( $submission_id );
		if ( is_wp_error( $submission ) ) {
			return $submission;
		}

		$drafts = $submission['drafts'] ?? array();
		if ( empty( $drafts ) ) {
			return new WP_Error( 'smashfire_no_draft', 'This submission has no generated draft to publish.' );
		}
		$latest_draft = end( $drafts );

		$post_id = wp_insert_post(
			array(
				'post_title'   => wp_strip_all_tags( $submission['headline'] ),
				'post_content' => $latest_draft['body_text'],
				'post_status'  => 'publish',
				'post_type'    => 'post',
			),
			true
		);
		if ( is_wp_error( $post_id ) ) {
			return $post_id;
		}

		// Private provenance, per the doc: never overwritten, never public.
		update_post_meta( $post_id, '_smashfire_pr_submission_id', $submission_id );
		update_post_meta( $post_id, '_smashfire_pr_sender_name', $submission['sender_name'] );
		update_post_meta( $post_id, '_smashfire_pr_sender_email', $submission['sender_email'] );
		update_post_meta( $post_id, '_smashfire_pr_sender_company', $submission['sender_company'] ?? '' );
		update_post_meta( $post_id, '_smashfire_pr_draft_generator', $latest_draft['generator'] );

		$live_url = get_permalink( $post_id );

		return $hub->mark_published( $submission_id, $post_id, $live_url );
	}
}
